from .models import User,GoogleUser
from website import create_app
import os
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint,render_template, request, flash, redirect, url_for, session
from flask_login import login_user,login_required,logout_user,current_user
from authlib.integrations.flask_client import OAuth
from datetime import timedelta

auth=Blueprint('auth',__name__)

# App config
app = create_app()
# Session config
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['GOOGLE_CLIENT_ID'] = "394635760882-2ovda99ifgb86fgj3cpdhuf3fmmdc17i.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'] ,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",
)    

@auth.route('/login-auth')
def login_auth():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth.route('/login/authorize')
def google_authorize():
    google = oauth.create_client('google') 
    token = google.authorize_access_token()  
    resp = google.get('userinfo') 
    user_info = resp.json()
    user = oauth.google.userinfo()  
    session['profile'] = user_info
    session.permanent = True 

    new_user=GoogleUser(email=user["email"],firstName=user["given_name"], lastName=user["family_name"])

    if not new_user.query.filter_by(email=user["email"]).first():
        db.session.add(new_user)
        db.session.commit()
        flash('Account Created Succesfully!', category='success')
        login_user(new_user,remember=True)
        return redirect(url_for('views.home'))      

    flash('Logged in successfully!',category='success') 
    login_user(new_user,remember=True)
    return redirect(url_for('views.home')) 


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        if len(email)==0 or len(password)==0: 
                flash('Fields cannot be empty!', category='error')
        else:
            user=User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!',category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home')) 
                else:
                    flash('Incorrect Password, try again!', category='error')
            else:
                flash('Email does not exist.', category='error')        

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('views.home'))     

@auth.route('/sign-up', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        firstName=request.form.get('firstName')
        lastName=request.form.get('lastName')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        user=User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            if len(email)==0 or len(firstName)==0 or len(lastName)==0 or len(password1)==0: 
                flash('Fields cannot be empty!', category='error')
            elif len(firstName)<2:
                flash('First Name Can\'t be too small', category='error')
            elif len(lastName)<2:
                flash('Last Name Can\'t be too small', category='error')
            elif len(password1)<8:
                flash('Password must be of 8 characters or more!', category='error')
            elif password1!=password2:
                flash('Password not matching!', category='error')
            else:
                new_user=User(email=email,firstName=firstName,password=generate_password_hash(password1,method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account Created Succesfully!', category='success')
                login_user(new_user,remember=True)
                return redirect(url_for('views.home')) 

    return render_template("sign_up.html", user=current_user) 
