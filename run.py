# coding=utf-8

import os 
import datetime
from flask import Flask, render_template, session, redirect, url_for, request, g, flash, send_from_directory
from flask_script import Manager
import sqlite3
from flask import g
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
import hashlib
from flask_migrate import Migrate, MigrateCommand
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'foolish'
app.config.from_object(__name__)

#集成python shell 调用shell时候将数据库对象直接导入shell
def make_shell_context():
    return dict(app=app, db=db, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

#404和500界面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html'), 500

#主页 todo
@app.route('/')
def index():
    tem = Post.query.all()  
    print type(tem)
    print tem[0].title
    print tem[4].file_img
    print tem[4].tags
    pmax = 9
    if False:
        session['new']=True
        return render_template('index.html',tem=tem,pmax=pmax,pg=1)
    else:
        return render_template('index.html',tem=tem,pmax=pmax,pg=1)

#管理员登陆 finish password = 000000
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
            print session['log']
            return redirect(url_for('admin'))
    return render_template('login.html')

#创建新博文 todo
@app.route('/new', methods=['GET', 'POST'])
def new():
    if session.get('log'):
        if request.method == 'POST':
            if request.form['editor'] and request.form['title']:
                abstract = abstr(request.form['editor'],request.form['img'])
                tags = (request.form['tags'] or '').replace('，',',')
                post = Post(title=request.form['title'], content=request.form['editor'], \
                    abstract=abstract, tags=tags,file_img = request.form['file'])
                db.session.add(post)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                '''
                cur.execute('select id from blog order by id desc limit 1')
                blog=cur.fetchall()
                blog=blog[0][0]
                tags=tags.split(',')
                for tag in tags:
                    cur.execute('insert into tag (tag, blog) values (?, ?)', (tag, blog))
                get_db().commit()
                '''
                return redirect(url_for('index',pg=1))
            elif request.form['editor']:
                return render_template('edit.html',content=request.form['editor'],img=request.form['img'])
        return render_template('edit.html')
    return redirect(url_for('page',pg=1))


#数据库模型
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.Text)
    abstract = db.Column(db.Text)
    tags = db.Column(db.String)
    file_img = db.Column(db.SmallInteger)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())




def abstr(text,img=""):
    text=text[:1200]
    text=text.replace(u'&nbsp;',u' ')
    text=text.replace(u'</p',u'\n<')
    text=text.replace(u'</b',u'\n<')
    text=text.replace(u'</h',u'\n<')
    text=text.replace(u'<br>',u'\n')
    def fn(x, y):
        if x[-1] == "<" and y != ">":
            return x
        else:
            return x+y
    text=reduce(fn,text)
    text=text.replace(u'<>',u'')
    text=text.replace(u'\n\n\n',u'\n')
    text=text.replace(u'\n\n',u'\n')
    print text
    text=text[:120]+'...'+'<center>'+img+'</center>'
    return text


if __name__ == '__main__':
    manager.run()