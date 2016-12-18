# coding=utf-8

import os 
import thread
import datetime
from flask import Flask, render_template, session, redirect, url_for, request, g, flash, send_from_directory, Markup
from flask_script import Manager
import sqlite3
from flask import g
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell, Server
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
    tem = Post.query.order_by(Post.id.desc()).all()
    print type(tem)
    blog_count = len(Post.query.all())
    pmax=((blog_count+7)/8 or 1)
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
            return redirect(url_for('new'))
    return render_template('login.html')

#分类博客
@app.route('/arch<int:arc>/<int:pg>')
def arch(arc,pg):
    tem = Post.query.filter_by(file_img=arc).order_by(Post.id.desc()).limit(8).offset(pg*8-8)
    try:
        blog_count = len(Post.query.filter_by(file_img=arc).all())
        pmax=((blog_count+7)/8 or 1)
    finally:
        pmax=pmax or 1
    if pg > pmax or pg < 1:
        return render_template('error.html'), 404
    else:
        return render_template('page.html',tem=tem,pmax=pmax,pg=pg)

#创建新博文 todo
@app.route('/new', methods=['GET', 'POST'])
def new():
    print session.get('log')
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
                return redirect(url_for('page',pg=1))
            elif request.form['editor']:
                return render_template('edit.html',content=request.form['editor'],img=request.form['img'])
        return render_template('edit.html')
    return redirect(url_for('page',pg=1))

#删除文章
@app.route('/dele/<int:bg_id>')
def dele(bg_id):
    if session.get('log'):
        try:
            article = Post.query.filter_by(id=bg_id).first()
            db.session.delete(article)
            db.session.commit()
        except:
            return redirect(url_for('page',pg=1))

#页数 每页显示8篇文章
@app.route('/page/<int:pg>')
def page(pg):
    tem = Post.query.order_by(Post.id.desc()).limit(8).offset(pg*8-8)
    print tem[0].file_img
    blog_count = len(Post.query.all())
    pmax=((blog_count+7)/8 or 1)
    if pg > pmax or pg < 1:
        return render_template('error.html'), 404
    else:
        return render_template('page.html',tem=tem,pmax=pmax,pg=pg)

@app.route('/lovetc')
def love():
    return render_template('fortc.html')
#时间搞事情 todo
#周一一定搞
@app.route('/edit/<int:bg_id>', methods=['GET', 'POST'])
def edit(bg_id):
    if session.get('log'):
        try:
            cont = Post.query.filter_by(id = bg_id).first()
        except:
            return redirect(url_for('page',pg=1))
        if request.method == 'POST':
            if request.form['editor'] and request.form['title']:
                cont = Post.query.filter_by(id = bg_id).first()
                abstract = abstr(request.form['editor'],request.form['img'])
                tags = (request.form['tags'] or '').replace('，',',')
                cont.title=request.form['title']
                cont.content=request.form['editor']
                cont.abstract=abstract
                cont.tags=tags
                cont.file_img = request.form['file']
                db.session.add(cont)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                return redirect(url_for('page',pg=1))
            elif request.form['editor']:
                return render_template('edit.html',content=request.form['editor'],img=request.form['img'])
        return render_template('edit.html',content=cont.content,title=cont.title,tags=cont.tags)
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
    

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)
    blog_comment = db.Column(db.Text)
    blog_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())



#博客详情页
@app.route('/article/<int:bg_id>', methods=['GET', 'POST'])
def article(bg_id):
    #todo 博客回复以及回复的回复的存入
    if request.method == 'POST':
        if request.form['comment']:
            author = request.form['author'] or u'访客'
            com = Comment()
            com.blog_comment = request.form['comment']
            com.author = author
            com.blog_id = bg_id
            db.session.add(com)
            db.session.commit()
            return redirect(url_for('article',bg_id=bg_id))
    #cont=cont 暂时取消评论 
    try:
        cont = Post.query.filter_by(id = bg_id).first()
    except:
        return render_template('error.html'), 404
    #todo 博客回复以及回复的回复的读取
    else:
        print 1
        tem = Comment.query.filter_by(blog_id=bg_id).order_by(Comment.id.desc()).all()
        print 2
        '''
        cur.execute(' SELECT content, date, author,id,reply FROM comm WHERE blog=? ORDER BY id DESC',(bg_id,))
        tem=cur.fetchall() or []
        tem=list(tem)
        tem=map(lambda x:list(x),tem)
        idli=map(lambda x:x[3],tem)
        t=0
        while t < len(tem):
            if type(tem[t][4]) == int:
                try:
                    reid = idli.index(tem[t][4])
                    tem[reid][4]=tem[reid][4] or []
                    tem[reid][4].insert(0,tem[t])
                    tem.pop(t)
                    idli.pop(t)
                    t -= 1
                finally:
                    pass
            t += 1
        '''
        return render_template('article.html',id=bg_id,cont=cont,tem=tem) 
#简介+缩略图
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
    text=text[:120]+'...'+'<center><img src='+img+'>+</center>'
    return text

#question:部署后session貌似没办法在各个页面之间传递，数据库迁移问题
#session有效传递，只是部署后一定要自己commit？？
if __name__ == '__main__':
    manager.run()