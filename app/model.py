'''
File: model.py
Authors: 
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Handles database connection and manipulation.
'''

from . import app, db

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
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
    email = db.Column(db.String(255), nullable=True, unique=True, index=True)
    password = db.Column(db.String(255))
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
    posts = db.relationship('Post', backref='user', order_by="desc(Post.id)")
    comments = db.relationship('Comment', backref='user',
            order_by="desc(Comment.id)")

    def __init__(self, password='', user_name=''):
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

    # Image relationships.  'Foreign key' construct to specify a
    # singular post cover.  'Primary key' to make explicit one to many
    # join condition.
    cover = db.relationship('Picture', uselist=False, foreign_keys=cover_id,
            post_update=True)
    gallery = db.relationship('Picture',
            primaryjoin="Post.id==Picture.post_id",
            order_by='Picture.position',
            collection_class=ordering_list('position', count_from=1))
    # 'And' construct used to specify that only top level comments
    # without a parent are listed here.  Each comment has its own
    # list of reply comments.
    comments = db.relationship('Comment', order_by="desc(Comment.id)",
            primaryjoin='and_(Post.id==Comment.post_id, '
            'Comment.parent_id==None)')
    # Post votes and total score.
    votes = db.relationship('Vote', backref='post')

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

class Comment(db.Model):
    """
    Post comments.
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    posted_at = db.Column(db.DateTime(timezone=True))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    children = db.relationship('Comment', backref=db.backref('parent',
            remote_side=[id]), order_by="desc(Comment.id)")

    def __init__(self, body='', posted_at = '', user_id=0, post_id=0,
            parent_id=None):
        self.body = body
        self.posted_at = posted_at
        self.user_id = user_id
        self.post_id = post_id
        self.parent_id = parent_id

    def __repr__(self):
        return '<id: {} parent_id: {} body: {}>'.format(self.id,
                self.parent_id, self.body)

class Vote(db.Model):
    """
    Post votes come in two variants: for / against.
    """
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
