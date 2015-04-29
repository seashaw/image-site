#!/usr/bin/env python3
'''
File: local.py
Authors: 
    2015-04-15 - C.Shaw <shaw.colin@gmail.com>
Description: 
    DEVELOPMENT ONLY
'''
from app import app, admin, FileView
app.config['SERVER_NAME'] = 'localhost:8080'
app.config['UPLOAD_FOLDER'] = \
        '/home/colin/workspace/angryhos/app/static/uploads'
admin.add_view(FileView(app.config["UPLOAD_FOLDER"], 'static/uploads/',
        name="Uploaded Files"))
app.config['DEBUG'] = True
