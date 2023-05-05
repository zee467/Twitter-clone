from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from werkzeug.security import check_password_hash, generate_password_hash
import cloudinary
from cloudinary.uploader import upload
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import os

# instantiate flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

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

# instantiate login manager
login_manager = LoginManager(app)


# initialize the app with the extension
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create user model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register form
class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'), Length(max=100, message='Your name cant be more than 100 characters.')])
    username = StringField('Username', validators=[InputRequired('Username is required.'), Length(max=30, message='Your username is too')])
    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    profile_image = FileField('Profile image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], message='Only images are allowed')])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[])
    remember = BooleanField("Remember me")



@app.route("/")
def index(): 
    form = LoginForm()

    if form.validate_on_submit():
        return f'<h1>Username: {form.username.data}, Password: {form.password.data}, Remember: {form.remember.data}</h1>'
    return render_template("index.html", form=form)


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            return "Login Failed"
        
        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for('profile'))
        return "Login Failed"

    return redirect(url_for('index'))

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

        new_user = User(name=form.name.data, username=form.username.data, password=generate_password_hash(form.password.data))
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    
    return render_template("register.html", form=form)


