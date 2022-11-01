from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
from flask_login import current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


db=SQLAlchemy()
DB_NAME='database'

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']= 'abcd@zephyr_SecretKey'
    app.config['SQLALCHEMY_DATABASE_URI']= f'sqlite:///{DB_NAME}.db'
    app.config['SQLALCHEMY_BINDS']={
        'database2':f'sqlite:///{DB_NAME}2.db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, GoogleUser

    create_database(app)

    
    #**************** Admin Dasboard ************
    class UserView(ModelView):
        can_create = False 
        can_edit = False 
        column_list = ['id','email','firstName','lastName','date']

        def is_accessible(self):
            if current_user.email=='admin0422@gmail.com':
                return current_user.is_authenticated


    admin = Admin(app,template_mode='bootstrap3')

    admin.add_view(UserView(User, db.session))
    admin.add_view(UserView(GoogleUser, db.session))
    #********************************************

    
    login_manager=LoginManager()
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        if GoogleUser.query.filter_by(email=email).first():
            return GoogleUser.query.filter_by(email=email).first()
        else:
            return User.query.filter_by(email=email).first()

    return app
    
def create_database(app):
    if not path.exists('website/'+ DB_NAME +'.db'):
        db.create_all(app=app)

    if not path.exists('website/'+ DB_NAME+'2'+'.db'):
        db.create_all(app=app)
