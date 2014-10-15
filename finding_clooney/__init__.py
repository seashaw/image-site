"""
File: __init__.py
Authors:
    2014-10-10 - C. Shaw
Description: 
    Initialization module for object tracker application.
    Order of initializations and imports are particular (sorry for
    the circular imports).
"""

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
from flask.ext.login import LoginManager

# Initialize the application.
app = Flask(__name__)

# Load configuration.
app.config.update(dict(
    # SQLAlchemy database connection address.
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL"),
    # Hardcoded URI to isolate local projects. HEROKU_POSTGRESQL_MAUVE_URL
    SQLALCHEMY_DATABASE_URI = 'postgres://bgxwtufpffxnff:bkh5prFQyHpC3VXL1N9W3h_wDZ@ec2-54-204-31-13.compute-1.amazonaws.com:5432/dbd3goi65hqu8d',

    SECRET_KEY = "In development.",
    SERVER_NAME = "www.findingclooney.com",

    # Mail settings.
    MAIL_SERVER = "smtp.googlemail.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = "",
    MAIL_PASSWORD = "",
    DEFAULT_MAIL_SENDER = "jamesshaw1962@gmail.com",

    ADMINS = ["jamesshaw1962@gmail.com"]
))

# Bcrypt object initialization.
bc = Bcrypt(app)

# Login object initialization.
lm = LoginManager()
lm.init_app(app)

# User loader callback for LoginManager.
@lm.user_loader
def loadUser(user_id):
    """
    Returns User object from database.
    """
    return User.query.get(user_id)

# Mail object initialization.
mail = Mail(app)

# SQLAlchemy object initialization..
db = SQLAlchemy(app)

# Object tracker model import.
from finding_clooney import model
from finding_clooney.model import User, Role, DBHandler

# Database handler class initialization.
dbh = DBHandler(db)

# Object tracker controller import.
import finding_clooney.controller
