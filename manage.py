#!/usr/bin/env python3
"""
Name: manage.py
Authors:
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Script to manage database migrations.
"""
from app import app, db, model
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# Migrate object initialization.
mig = Migrate(app, db)

# Script manager setup.
man = Manager(app)
man.add_command('db', MigrateCommand)

if __name__ == '__main__':
    man.run()
