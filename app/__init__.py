"""
File: __init__.py
Authors:
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Initialization module for object tracker application.
    Order of initializations and imports is particular.
"""

import os
from collections import namedtuple
from functools import partial

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask.ext.mail import Mail
from flask.ext.login import LoginManager, current_user
from flask.ext.principal import (Principal, identity_loaded, Permission,
        RoleNeed, UserNeed)
from flask.ext.admin import Admin
from flask.ext.admin.contrib.fileadmin import FileAdmin

# Initialize the application.
app = Flask(__name__)

def getPassword(pw_file):
    """
    Function to get email password from local file.
    """
    # Open file for reading.
    file = open(pw_file, mode='r')
    # Read one line and strip newline character.
    email_password = file.read().strip()
    # Close the file and return password.
    file.close()
    return email_password

# Load configuration.
app.config.update(dict(
    # SQLAlchemy database connection address.
    SQLALCHEMY_DATABASE_URI = 'postgres://angryhos:hobag@localhost/angryhos',

    SECRET_KEY = "In development.",
    #SERVER_NAME = "www.angryhos.com",
    SERVER_NAME = 'localhost:8080',
    # Remove DEBUG line for production.
    DEBUG = True,

    # Mail settings.
    MAIL_SERVER = "smtp.zoho.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = "noreply@angryhos.com",
    MAIL_PASSWORD = getPassword("pw"),

    ADMIN_EMAIL = "administrator@angryhos.com",

    # Upload settings.
    UPLOAD_FOLDER = '/home/colin/workspace/angryhos/app/static/uploads',
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5MB
))

# Bcrypt object initialization.
bc = Bcrypt(app)

# Login object initialization.
lm = LoginManager()
lm.init_app(app)

# Principal object initialization.
principal = Principal(app)

# Mail object initialization.
mail = Mail(app)

# SQLAlchemy object initialization.
db = SQLAlchemy(app)

# Model class imports.
from .model import User, Role, Post, Picture

# User loader callback for LoginManager.
@lm.user_loader
def loadUser(user_id):
    """
    Returns User object from database.
    """
    return User.query.get(user_id)

"""
Posting and editing permissions.
"""

BlogPostNeed = namedtuple('blog_post', ['method', 'value'])
EditBlogPostNeed = partial(BlogPostNeed, 'edit')

class EditBlogPostPermission(Permission):
    """
    Permission definition for editing blog posts.
    """
    def __init__(self, post_id):
        need = EditBlogPostNeed(str(post_id))
        super(EditBlogPostPermission, self).__init__(need)

# User information provider for Principal.
@identity_loaded.connect_via(app)
def onIdentityLoaded(sender, identity):
    """
    Connects to the identity-loaded signal to add additional information to
    the Identity instance, like user roles.
    """
    # Set the identity user object.
    identity.user = current_user

    # Add UserNeed to the identity.
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(str(current_user.id)))

    # Update identity with list of roles that User provides.
    # Refers to relationship 'roles' from User model.
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Update identity with list of posts that user authored.
    # Refers to relationship 'posts' from User model.
    if hasattr(current_user, 'posts'):
        for post in current_user.posts:
            identity.provides.add(EditBlogPostNeed(str(post.id)))

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
admin.add_view(FileView(app.config["UPLOAD_FOLDER"], '/static/uploads/',
        name="Uploaded Files"))
