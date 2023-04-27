from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length
import os


# instantiate flask app
app = Flask(__name__)
# app configurations
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# initialize the app with the extension
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))


# Register form
class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'), Length(max=100, message='Your name cant be more than 100 characters.')])
    username = StringField('Username', validators=[InputRequired('Username is required.'), Length(max=30, message='Your username is too')])
    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    profile_image = FileField('Profile image')




@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/timeline")
def timeline():
    return render_template("timeline.html")

@app.route("/register")
def register():
    form = RegisterForm()
    return render_template("register.html", form=form)


