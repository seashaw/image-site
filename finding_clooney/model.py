'''
File: model.py
Authors: 
    2014-10-10 - C. Shaw
Description: Handles database connection and manipulation.
'''

from . import app, db
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask.ext.login import UserMixin

"""
Relation table to link users and roles.
"""

user_roles = db.Table('user_roles',
        db.Column('user_id',
            db.Integer(),
            db.ForeignKey('users.id')),
        db.Column('role_id',
            db.Integer(),
            db.ForeignKey('roles.id')))

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
    active = db.Column(db.Boolean(), default=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    user_name = db.Column(db.String(80), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, email, password, active, first_name, last_name, 
            user_name, roles):
        self.email = email
        self.password = password
        self.active = active
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name

    def __repr__(self):
        return '<id %r>' % self.id

class Role(db.Model):
    """
    Table to define User roles.
    """

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def __repr__(self):
        return '<id %r>' % self.id

class Table(db.Model):
    """
    Schema for table datatable.
    """
    
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(80))
    creator = db.Column(db.String(80))
    owner = db.Column(db.String(80))
    
    def __init__(self, table_name, creator, owner):
        self.table_name = table_name
        self.creator = creator
        self.owner = owner

    def __repr__(self):
        return '<id %r>' % self.id

class TableUser(db.Model):
    """
    Table group datatable, listing users authorized to view and/or modify 
    given table.
    """
    
    __tablename__ = 'table_users'
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, ForeignKey('tables.id'))
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    write = db.Column(db.Integer)

    def __init__(self, table_id, user_id, write):
        self.table_id = table_id
        self.user_id = user_id
        self.write = write

    def __repr__(self):
        return '<id %r>' % self.id

class SumResult(db.Model):
    """
    Table to store sums of jQuery calls.
    """

    __tablename__ = 'sum_results'
    id = db.Column(db.Integer, primary_key=True)
    sum = db.Column(db.Integer)

    def __init__(self, sum):
        self.sum = sum

class DBHandler:
    """
    A custom wrapper class over SQLAlchemy, handles database CRUD operations as
    well as error reporting (eventually).
    """
    def __init__(self, db):
        self.db = db

    def insertUser(self, user):
        """
        Inserts new user record into table 'users'.
        """
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return False
        return True

    def insertSum(self, sum):
        """
        Inserts new records into table 'sum_results'.
        """
        try:
            db.session.add(sum)
            db.session.commit()
        except Exception as e:
            # some error logging...
            return False
        return True

    def fetchAllSums(self):
        """
        Fetchs all sum results from table 'sum_results'.
        """
        return db.engine.execute('SELECT sum FROM sum_results')

    def fetchAllUserNames(self):
        """
        Fetches all user names from table 'users'.
        """
        #all_users = User.query.all() # SQLAlchemy select.
        return db.engine.execute('SELECT user_name FROM users')
