#uuid
import uuid
'''for db pupose'''
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# contact model

class Contacts(db.Model):
    '''sno,name,phone_num,msg,date,email'''
    '''by default nullable=True which means user can define null value'''
    sno = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=True)

# post model

class Posts(db.Model):
    '''sno,title,slug,subheading,content,date,img_file'''
    '''by default nullable=True which means user can define null value'''
    sno = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    subheading = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.JSON, nullable=True, default={})