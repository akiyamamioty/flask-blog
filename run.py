# coding=utf-8

import os 
from flask import Flask
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    pass

if __name__ == '__main__':
    manager.run()