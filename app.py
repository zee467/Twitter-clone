from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# instantiate flask app
app = Flask(__name__)
# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

# initialize the app with the extension
db = SQLAlchemy(app)
migrate = Migrate(app)


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


