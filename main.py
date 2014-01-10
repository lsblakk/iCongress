import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import time
from flask.ext.login import LoginManager, UserMixin
from flaskext.browserid import BrowserID
from flask.ext.sqlalchemy import SQLAlchemy

## SETUP
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flaskr.db'
db = SQLAlchemy(app)
app.config.from_object(__name__)

app.config['BROWSERID_LOGIN_URL'] = "/login"
app.config['BROWSERID_LOGOUT_URL'] = "/logout"
app.config['SECRET_KEY'] = "deterministic"
app.config['TESTING'] = True

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.UnicodeText, unique=True)
    firstname = db.Column(db.Unicode(40))
    lastname = db.Column(db.Unicode(40))
    date_register = db.Column(db.Integer)
    bio = db.Column(db.Text)
    facebook = db.Column(db.Unicode(1000))
    twitter = db.Column(db.Unicode(1000))
    website = db.Column(db.Unicode(1000))
    image = db.Column(db.LargeBinary)

    def __init__(self, email, firstname=None, lastname=None, date_register=None, bio=None, facebook=None, twitter=None, 
                    website=None, image=None):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.date_register = time.time()
        self.bio = bio
        self.facebook = facebook
        self.twitter = twitter
        self.website = website
        self.image = image
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email

### Login Functions ###
def get_user_by_id(id):
    """
    Given a unicode ID, returns the user that matches it.
    """
    return User.query.get(id)
    """
    for row in db.session.query(User).filter(User.id == id):
        if row is not None:
            print "get_user_by_id - " + str(type(row.User)) + " - " + str(row.User)
            return row.User
    return None"""

def create_browserid_user(kwargs):
    """
    Takes browserid response and creates a user.
    """
    if kwargs['status'] == 'okay':
        user = User(kwargs['email'])
        db.session.add(user)
        db.session.commit()
        print "create_browserid_user - " + str(type(user)) + " - " + str(user)
        return user
    else:
        return None

def get_user(kwargs):
    """
    Given the response from BrowserID, finds or creates a user.
    If a user can neither be found nor created, returns None.
    """
    u = User.query.filter(db.or_(
        User.id == kwargs.get('id'),
        User.email == kwargs.get('email')
    )).first()
    if u is None: # user didn't exist in db
        return create_browserid_user(kwargs)
    return u
    """
    # try to find the user
    for row in db.session.query(User).filter(User.email == kwargs.get('email')):
        if row is not None:
            print "get_user - " + str(type(row.User)) + " - " + str(row.User)
            return row.User
    for row in db.session.query(User).filter(User.id == kwargs.get('id')):
        if row is not None:
            print "get_user - " + str(type(row.User)) + " - " + str(row.User)
            return row.User
    # try to create the user
    return create_browserid_user(kwargs)"""

login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

browserid = BrowserID()
browserid.user_loader(get_user)
browserid.init_app(app)

### Routing ###
@app.route('/')
def home():
    return render_template('index.html')

### Admin Tools ###
@app.route('/show_db')
def show_db():
    users = []
    for user in db.session.query(User):
        users.append(dict(id=user.id, email=user.email, fisrtname=user.firstname, lastname=user.lastname, date_register=user.date_register))
    return render_template('show_db.html', users=users)


if __name__ == '__main__':
    app.run()