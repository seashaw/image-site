#!/usr/bin/env python3
"""
Name: manage.py
Authors:
    2014-10-10 - C. Shaw
Description: Script to manage database migrations.
"""
from finding_clooney import app, db, model
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# Migrate object initialization.
mig = Migrate(app, db)

# Script manager setup.
man = Manager(app)
man.add_command('db', MigrateCommand)

if __name__ == '__main__':
    man.run()
