#!/usr/bin/env python3
'''
File: wsgi.py
Authors:
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: 
    Application entry point for uWSGI.
'''
from app import app, admin, FileView
app.config['SERVER_NAME'] = 'image-site.colinshaw.org'
app.config['UPLOAD_FOLDER'] =  \
        '/home/colin/applications/image-site/app/static/uploads'
admin.add_view(FileView(app.config["UPLOAD_FOLDER"], '/static/uploads/',
        name="Uploaded Files"))
