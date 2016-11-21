# coding=utf-8

import os 
from flask import Flask, render_template, session, redirect, url_for, request, g, flash, send_from_directory
from flask_script import Manager
import sqlite3
from flask import g
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
import hashlib
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'foolish'
db = SQLAlchemy(app)
app.config.from_object(__name__)

#集成python shell 调用shell时候将数据库对象直接导入shell
def make_shell_context():
    return dict(app=app, db=db, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))

#404和500界面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html'), 500

#主页
@app.route('/')
def index():
    tem = Post.query.all()  
    pmax = 9
    if False:
        session['new']=True
        return render_template('index.html',tem=tem,pmax=pmax,pg=1)
    else:
        return render_template('index.html',tem=tem,pmax=pmax,pg=1)

#管理员登陆
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass_word = request.form['passwd']
        m = hashlib.md5()
        if not pass_word:
            pass_word = ''
        else:
            pass_word += '1396'
        m.update(pass_word)
        if m.hexdigest()=='01bf2bf3375b3fbaf8d2dac6dad08c84':
            session['log'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')


#数据库模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True)

if __name__ == '__main__':
    manager.run()