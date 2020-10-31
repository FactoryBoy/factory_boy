# Copyright: See the LICENSE file.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(1000))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))

    def __init__(self, message, user):
        self.message = message
        self.user = user

    def __repr__(self):
        return f'<Log for {self.user!r}: {self.message}>'
