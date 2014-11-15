#!/usr/bin/env python3
'''
File: wsgi.py
Authors:
    2014-11-14 - C.Shaw <shaw.colin@gmail.com>
Description: Launch web application.
'''

from app import app
if __name__ == '__main__':
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.run(debug=True)
