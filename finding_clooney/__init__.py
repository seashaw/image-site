"""
File: __init__.py
Authors:
    2014-10-10 - C.Shaw <shaw.colin@gmail.com>
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

# Initialize the application.
app = Flask(__name__)

# Load configuration.
app.config.update(dict(
    # SQLAlchemy database connection address.
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL"),
    # Hardcoded URI to isolate local projects. HEROKU_POSTGRESQL_MAUVE_URL
    SQLALCHEMY_DATABASE_URI = ('postgres://bgxwtufpffxnff:bkh5prFQyHpC3VXL1N9W'
        '3h_wDZ@ec2-54-204-31-13.compute-1.amazonaws.com:5432/dbd3goi65hqu8d'),

    SECRET_KEY = "In development.",
    SERVER_NAME = "www.findingclooney.com",
    #SERVER_NAME = '168.235.67.254:8000',

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

# Principal object initialization.
principal = Principal(app)

# Mail object initialization.
mail = Mail(app)

# SQLAlchemy object initialization..
db = SQLAlchemy(app)

# Object tracker model import.
from finding_clooney import model
from finding_clooney.model import User, Role, Post, DBHandler

# Database handler class initialization.
dbh = DBHandler(db)

# Admin object initialization.
admin = Admin(app)

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
        need = EditBlogPostNeed(post_id)
        super(EditBlogPostPermission, self).__init__(need)

# User information provider for Principal.
@identity_loaded.connect_via(app)
def onIdentityLoad(sender, identity):
    """
    Connects to the identity-loaded signal to add additional information to
    the Identity instance, like user roles.
    """
    # Set the identity user object.
    identity.user = current_user

    # Add UserNeed to the identity.
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Update identity with list of roles that User provides.
    # Refers to relationship 'roles' from User model.
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Update identity with list of posts that user authored.
    # Refers to relationship 'posts' from User model.
    if hasattr(current_user, 'posts'):
        for post in current_user.posts:
            identity.provides.add(EditBlogPostNeed(post.id))

# Object tracker controller import.
import finding_clooney.controller
from finding_clooney.controller import (UsersAdminView, RolesAdminView,
        PostsAdminView)
admin.add_view(UsersAdminView(User, db.session, name='Users'))
admin.add_view(RolesAdminView(Role, db.session, name='Roles'))
admin.add_view(PostsAdminView(Post, db.session, name='Posts'))
