from wtforms import Form, StringField, TextAreaField, PasswordField, validators, EmailField

#Register Form
class RegisterForm(Form):
    name = StringField("Name and Surname", validators=[validators.DataRequired(message="Please type your name"), validators.Length(min=3,max=30)])
    email = EmailField("Email", validators=[validators.DataRequired(), validators.Length(max=50), validators.Email(message="Please type a correct email")])
    username = StringField("Username", validators=[validators.DataRequired(), validators.Length(min=5,max=30)])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Password is a necessity"), validators.EqualTo("confirm",message="Password must match")])
    confirm = PasswordField("Confirm password")

#Login Form
class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")

#Article Form
class ArticleForm(Form):
    title = StringField("Title", validators=[validators.Length(4,20)])
    content = TextAreaField("Article Content", validators = [validators.Length(10)])

