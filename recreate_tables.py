#!/usr/bin/env python3
from app import db, bc
import app.model
from app.model import User, Role
import os
import shutil
from datetime import datetime
from pytz import utc
# Drop all database tables.
print("Dropping and recreating database tables.")
db.drop_all()
db.create_all()
# Remove all user uploads.
print("Removing and recreating upload folder.")
shutil.rmtree('app/static/uploads/1/')
os.mkdir('app/static/uploads/1')
os.chmod('app/static/uploads/1', mode=0o777)
# Create default user.
print("Creating new user.")
user = User(password=bc.generate_password_hash('la73ralu5', rounds=12),
        user_name='cshaw')
# Creating roles.
print("Creating roles.")
active_role = Role(name="Active", description="Active user.")
verified_role = Role(name="Verified",
        description="User with a verified email.")
admin_role = Role(name="Administrator", description="Administrator.")
print("Adding roles to session.")
db.session.add(admin_role)
db.session.add(active_role)
db.session.add(verified_role)
db.session.flush()
# Add roles to user object.
print("Adding roles to user.")
user.roles.append(admin_role)
user.roles.append(active_role)
user.roles.append(verified_role)
print("Adding user to session.")
db.session.add(user)
print("Commiting session to database.")
db.session.commit()
