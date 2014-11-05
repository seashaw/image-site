#!/usr/bin/env python3
'''
File: run.py
Authors:
    2014-10-10 - C. Shaw
Description: Launch web application.
'''

from finding_clooney import app
if __name__ == '__main__':
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.run(debug=True)
