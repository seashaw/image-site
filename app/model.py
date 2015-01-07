'''
File: model.py
Authors: 
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Handles database connection and manipulation.
'''

from . import app, db

from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.login import UserMixin

"""
Relation tables.
"""

# Link tables 'users' and 'roles'.
user_roles = db.Table('user_roles',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

"""
Classes to define database table schema.
"""

class User(db.Model, UserMixin):
    """
    Defines schema for user datatable.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    user_name = db.Column(db.String(80), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    roles = db.relationship('Role', secondary=user_roles,
            backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='users', order_by="Post.id")
    nonce = db.relationship('Nonce', uselist=False, backref="users")

    def __init__(self, email='', password='', active=False, first_name='',
            last_name='', user_name='', roles=[], posts=[]):
        self.email = email
        self.password = password
        self.active = active
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name

    def __repr__(self):
        return '<id: {} username: {}>'.format(self.id, self.user_name)

class Role(db.Model):
    """
    Table to define User roles.
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name='', description=''):
        self.name = name
        self.description = description
        
    def __repr__(self):
        return '<id: {} name: {}>'.format(self.id, self.name)

class Post(db.Model):
    """
    Blog posts.
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True)
    subtitle = db.Column(db.String(80))
    body = db.Column(db.Text)
    posted_at = db.Column(db.DateTime()) # All datetime entries should be UTC.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    pictures = db.relationship('Picture', backref='posts')

    def __init__(self, title='', subtitle='', body='', posted_at='',
            user_id=0):
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.posted_at = posted_at
        self.user_id = user_id
        
    def __repr__(self):
        return '<id: {} title: {}>'.format(self.id, self.title)

class Picture(db.Model):
    """
    Blog post pictures.
    """
    __tablename__ = 'pictures'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))
    caption = db.Column(db.String(80))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    
    def __init__(self, filename='', caption=filename):
        self.filename = filename
        self.caption = caption

    def __repr__(self):
        return '<id: {} filename: {}>'.format(self.id, self.filename)

class Nonce(db.Model):
    """
    Cryptographic nonces with time expiration, used for registration
    and confirmation.
    """
    __tablename__ = 'nonces'
    id = db.Column(db.Integer, primary_key=True)
    nonce = db.Column(db.String(), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    issued_at = db.Column(db.DateTime()) # All datetime entries should be UTC.
    
    def __init__(self, nonce_id='', user_id=0, issued_at='', nonce=''):
        self.nonce_id = nonce_id
        self.user_id = user_id
        self.issued_at = issued_at
        self.nonce = nonce
