import datetime
from . import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    __tablename__='User'
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    firstName=db.Column(db.String(150))
    lastName=db.Column(db.String(150))
    date=db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def get_id(self):
        return str(self.email)

class GoogleUser(db.Model,UserMixin):
    __tablename__='GoogleUser'
    __bind_key__='database2'
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(100),unique=True)
    firstName=db.Column(db.String(150))
    lastName=db.Column(db.String(150))
    date=db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def get_id(self):
        return str(self.email)