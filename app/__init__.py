"""
File: __init__.py
Authors:
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Initialization module for object tracker application.
    Order of initializations and imports is particular.
"""

import os
from datetime import datetime

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
from flask.ext.login import LoginManager, current_user
from flask.ext.admin import Admin
from flask.ext.admin.contrib.fileadmin import FileAdmin

# Initialize the application.
app = Flask(__name__)
# Add now to jinja globals for dynamic year footer.
app.jinja_env.globals.update(now=datetime.now())

def getPassword():
    """
    Function to get email password from local file.
    """
    # Open file for reading.
    file = open('pw', mode='r')
    # Read first line and strip newline character.
    email_password = file.read().strip()
    # Close the file and return password.
    file.close()
    return email_password

# Load configuration.
app.config.update(dict(
    # SQLAlchemy database connection address.
    SQLALCHEMY_DATABASE_URI = 'postgresql://angryhos:hobag@localhost/angryhos',

    SECRET_KEY = "In development.",

    # Mail settings.
    MAIL_SERVER = "smtp.zoho.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = "noreply@angryhos.com",
    MAIL_PASSWORD = getPassword(),

    ADMIN_EMAIL = "administrator@angryhos.com",

    # Set of allowed file extensions.
    EXTENSIONS = set(["png", "jpg", "jpeg", "gif"]),

    # Upload settings.
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5MB
))

# Bcrypt object initialization.
bc = Bcrypt(app)

# Mail object initialization.
mail = Mail(app)

# SQLAlchemy object initialization.
db = SQLAlchemy(app)

# Model class imports.
from .model import User, Role, Post, Picture

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

# Principal and role based access control import.
from . import roles

# Controller import.
from . import controller

# Admin view import.
from .admin import (HomeView, UsersView, RolesView, PostsView, PicturesView,
        FileView)

# Admin object initialization.
admin = Admin(app, index_view=HomeView(), name="Angry Hos")

admin.add_view(UsersView(User, db.session, name='Users'))
admin.add_view(RolesView(Role, db.session, name='Roles'))
admin.add_view(PostsView(Post, db.session, name='Posts'))
admin.add_view(PicturesView(Picture, db.session, name='Pictures'))
