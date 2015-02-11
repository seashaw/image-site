'''
File: model.py
Authors: 
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Handles database connection and manipulation.
'''

from . import app, db

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list

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
    User information.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    user_name = db.Column(db.String(80), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    confirm_nonce = db.Column(db.String(), unique=True, nullable=True)
    confirm_nonce_issued_at = db.Column(db.DateTime(timezone=True),
            nullable=True)
    reset_nonce = db.Column(db.String(), unique=True, nullable=True)
    reset_nonce_issued_at = db.Column(db.DateTime(timezone=True),
            nullable=True)

    roles = db.relationship('Role', secondary=user_roles,
            backref=db.backref('users', lazy='dynamic'))
    postings = db.relationship('Post', backref='users', order_by="Post.id")

    def __init__(self, email='', password='', active=True, user_name='',
            roles=[], postings=[]):
        self.email = email
        self.password = password
        self.user_name = user_name

    def __repr__(self):
        return '<id: {} username: {}>'.format(self.id, self.user_name)

class Role(db.Model):
    """
    User roles.
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
    title = db.Column(db.String(80))
    subtitle = db.Column(db.String(80), nullable=True)
    body = db.Column(db.Text, nullable=True)
    posted_at = db.Column(db.DateTime(timezone=True))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cover_id = db.Column(db.Integer, db.ForeignKey('pictures.id',
            use_alter=True, name='fk_post_cover_id'))
    cover = db.relationship('Picture', uselist=False, foreign_keys=cover_id,
            post_update=True)
    gallery = db.relationship('Picture',
            primaryjoin="Post.id==Picture.post_id",
            order_by='Picture.position',
            collection_class=ordering_list('position'))

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
    title = db.Column(db.String(80))
    position = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, filename='', title=''):
        self.filename = filename
        if title == '':
            self.title = filename 
        else:
            self.title = title

    def __repr__(self):
        return '<id: {} filename: {} position: {}>'.format(
                self.id, self.filename, self.position)
