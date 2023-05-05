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
from datetime import datetime
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
login_manager.login_view = 'login'  # tells flask-login where to redirect the user if they are trying to access an unauthorized page


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
    join_date = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(user_id):
    # Logic to load a user from the database based on user_id
    return User.query.get(int(user_id))


# Register form
class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'), Length(max=100, message='Your name can\'t be more than 100 characters.')])
    username = StringField('Username', validators=[InputRequired('Username is required.'), Length(max=30, message='Your username has too many characters.')])
    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    profile_image = FileField('Profile image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], message='Only images are allowed.')])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Username is required.'), Length(max=30, message='Your username has too many characters.')])
    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    remember = BooleanField("Remember me")



@app.route("/")
def index(): 
    form = LoginForm()

    return render_template("index.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            return render_template("index.html", form=form, message="Login Failed!")
        
        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for('profile'))
        return "Login Failed"

    # executes if the form's validation returns False or if it is a get request
    return render_template("login.html", form=form)

@app.route("/profile")
@login_required
def profile():
    # Get the current user's file path from the database
    file_path = current_user.image 

    # Generate the Cloudinary URL for the file
    file_url = cloudinary.CloudinaryImage(file_path).build_url()
    return render_template("profile.html", current_user=current_user, file_url=file_url)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.html'))

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
            print(upload_result)

        new_user = User(name=form.name.data, username=form.username.data, image=upload_result['secure_url'], \
                        password=generate_password_hash(form.password.data), join_date=datetime.now())
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    
    return render_template("register.html", form=form)


