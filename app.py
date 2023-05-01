from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length
import cloudinary
from cloudinary.uploader import upload
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# instantiate flask app
app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name= os.getenv('CLOUD_NAME'),
    api_key= os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET'),
    secure=True
)


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
    profile_image = FileField('Profile image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], message='Only images are allowed')])



@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/timeline")
def timeline():
    return render_template("timeline.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # get the file from the request 
        file_to_upload = request.files['profile_image']

        if file_to_upload:
            # Extract the filename from the file path
            filename = file_to_upload.filename
            file_path = f"twitter_clone/{filename}"
            
            # Upload the file to Cloudinary
            upload_result = upload(file_to_upload, public_id=file_path)

        return f"Full Name: {form.name.data}, Username: {form.username.data}"

    
    return render_template("register.html", form=form)


