from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# instantiate flask app
app = Flask(__name__)
# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

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
    return render_template("register.html")


