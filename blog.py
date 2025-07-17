from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from form import RegisterForm, LoginForm, ArticleForm
from functools import wraps


app = Flask(__name__)
app.secret_key = 'e3a2d0726070682b6dd5c91cec000917'

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "blog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app=app)


#Login Check
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        return redirect("login")
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        
        query = "insert into users (name, email, username, password) values (%s, %s, %s, %s)"

        cursor.execute(query, (name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        
        flash("Your registration is completed.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()

        query = "select username,password from users where username = %s"
        cursor.execute(query, (username,))
        response = cursor.fetchone()
        cursor.close()
        
        if sha256_crypt.verify(password, response["password"]):
            session["logged_in"] = True
            session["username"] = username

            flash("Your login is completed.", "success")
            return redirect(url_for("index"))
        flash("Username or password is wrong!", "danger")
        return redirect(url_for("login"))
    return render_template("login.html", form = form)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()

    query = "SELECT * FROM articles ORDER BY id DESC"
    cursor.execute(query)
    result = cursor.fetchall()

    return render_template("articles.html", articles = result)

@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()
    
    query = "SELECT * from articles WHERE id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchone()

    if result:
        return render_template("article.html", article=result)
    return render_template("article.html")

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    query = "SELECT * FROM articles WHERE author = %s"
    cursor.execute(query,(session["username"],))
    result = cursor.fetchall()

    if result:
        return render_template("dashboard.html", articles=result)
    return render_template("dashboard.html")

@app.route("/addarticle", methods = ["GET", "POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)
    
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()
        query = "insert into articles (title, author, content) values (%s, %s, %s)"
        cursor.execute(query, (title, session["username"], content))
        mysql.connection.commit()
        cursor.close()

        flash("Article has been added.", "success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html", form = form)

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    query = "Select * from articles where author = %s and id = %s"
    cursor.execute(query,(session["username"],id))
    result = cursor.fetchone()

    if result:
        query = "Delete from articles Where id = %s"
        cursor.execute(query)
        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    flash("There is no so-called article, or you do not have permission to delete it.","danger")
    return redirect(url_for("index"))

@app.route("/edit/<string:id>", methods = ["GET", "POST"])
@login_required
def edit(id):
    cursor = mysql.connection.cursor()
    query = "Select * from articles where id = %s and author = %s"
    cursor.execute(query,(id,session["username"]))
    result = cursor.fetchone()

    if not result:
        flash("There is no so-called article, or you do not have permission to edit it.","danger")
        return redirect(url_for("index"))

    form = ArticleForm(request.form)
    
    if request.method == "POST":
        query = "Update articles set title=%s, content=%s WHERE id = %s"
        cursor.execute(query,(form.title.data,form.content.data,id))
        mysql.connection.commit()
        
        return redirect(url_for("dashboard"))
    form.title.data = result["title"]
    form.content.data = result["content"]    
    return render_template("edit.html", form=form)

@app.route("/search", methods = ["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = "%"+request.form.get("keyword")+"%"
        cursor = mysql.connection.cursor()

        query = "select * from articles where title like %s"
        cursor.execute(query,(keyword,))
        result = cursor.fetchall()

        if result:
            return render_template("articles.html", articles = result)
        else:
            flash("No results found for your search.", "warning")
            return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True) #For devoloping