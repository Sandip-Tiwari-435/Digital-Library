from website import create_app
from flask import Blueprint, flash, render_template, redirect, send_from_directory, abort, request
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from .models import User,GoogleUser
import os
import html2text
import json

views = Blueprint('views',__name__)
app = create_app()

from os.path import join, dirname, realpath

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads')
app.config['FILE_UPLOADS']=UPLOADS_PATH
app.config["ALLOWED_FILE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "PDF", "PPT", "DOCX", "DOC", "PPTX", "TXT"]
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config["MAX_FILE_FILESIZE"] = 0.5 * 1024 * 1024





# ****************************
# create user's directory 
# ****************************

@views.route('/')
@login_required
def home():
    if not os.path.isdir(app.config["FILE_UPLOADS"]):
        os.mkdir(app.config["FILE_UPLOADS"])
    subdir=current_user.email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
    if not os.path.isdir(user_folder):
        os.mkdir(user_folder)
    public=os.path.join(user_folder, "public")
    private=os.path.join(user_folder, "private")
    friends=os.path.join(user_folder, "friends")
    if not os.path.isdir(public):
        os.mkdir(public)
    if not os.path.isdir(private):
        os.mkdir(private)
    if not os.path.isdir(friends):
        os.mkdir(friends)

    return render_template("home.html",user=current_user)

# ****************************
# ****************************







# ****************************
# Upload-Download
# ****************************

def allowed_file_filesize(filesize):

    if int(filesize) <= app.config["MAX_FILE_FILESIZE"]:
        return True
    else:
        return False

def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False

@views.route("/upload-file", methods=["GET", "POST"])
@login_required
def upload_file():

    subdir=current_user.email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
    public=os.path.join(user_folder, "public")
    private=os.path.join(user_folder, "private")

    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:
                if not allowed_file_filesize(request.cookies["filesize"]):
                    flash("Filesize exceeded maximum limit")
                    return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                flash('Empty File!', category='error')
                return redirect(request.url)

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                if request.form["directory"]=="public":
                    file.save(os.path.join(public,filename))
                else:
                    file.save(os.path.join(private,filename))
                flash('file uploaded successfully!', category='success')
                return redirect(request.url)
            else:
                flash("That file extension is not allowed", category='error')
                return redirect(request.url)

    return render_template("upload_file.html",user=current_user,directory=user_folder,files1=os.listdir(private),files2=os.listdir(public))

@views.route("/get-file-private/<string:file_name>")
@login_required
def get_file1(file_name):
    try:
        subdir=current_user.email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        private=os.path.join(user_folder, "private")
        return send_from_directory(private, path=file_name, as_attachment=False)
    except FileNotFoundError:
        return "File Not Fouund!"

@views.route("/delete-file-private/<string:file_name>")
@login_required
def delete_file1(file_name):
    try:
        subdir=current_user.email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        private = os.path.join(user_folder,"private")
        file=os.path.join(private,file_name)
        os.remove(file)
        flash(f"{file_name} has been deleted", category='warning')
        return redirect("/upload-file")
    except:
        flash(f"{file_name} Not Found! (or has been removed!)", category='error')
        return redirect("/upload-file")


@views.route("/get-file-public/<string:file_name>")
@login_required
def get_file2(file_name):
    try:
        subdir=current_user.email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        public=os.path.join(user_folder, "public")
        return send_from_directory(public, path=file_name, as_attachment=False)
    except FileNotFoundError:
        return "File Not Fouund!"

@views.route("/delete-file-public/<string:file_name>")
@login_required
def delete_file2(file_name):
    try:
        subdir=current_user.email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        public = os.path.join(user_folder,"public")
        file=os.path.join(public,file_name)
        os.remove(file)
        flash(f"{file_name} has been deleted", category='warning')
        return redirect("/upload-file")
    except:
        flash(f"{file_name} Not Found! (or has been removed!)", category='error')
        return redirect("/upload-file")

#***************************
#***************************










#***********************************
# search user and user's file (search bar)
#***********************************

@views.route("/search-user",methods=['GET','POST'])
@login_required
def search_user():
    subdir=current_user.email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)

    public=os.path.join(user_folder, "public")

    if request.method == "POST":
        email=request.form.get('email')
        user=User.query.filter_by(email=email).first()
        if user:
            subdir=email
            user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
            public=os.path.join(user_folder, "public")
            flash("User Found!",category="success")
            return render_template("visit_user.html",user=current_user,visited_user=user,directory=user_folder,files2=os.listdir(public),email=email,friendStat=-1)

        user=GoogleUser.query.filter_by(email=email).first()
        if user:
            subdir=email
            user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
            public=os.path.join(user_folder, "public")
            flash("User Found!",category="success")
            return render_template("visit_user.html",user=current_user,visited_user=user,directory=user_folder,files2=os.listdir(public),email=email,friendStat=-1)
        else:
            flash("There is no user with the given email!", category="warning")    
            return redirect(request.url)
    return render_template("home.html",user=current_user)

@views.route("/get-user-file/<string:visited_user_email>/<string:file_name>")
@login_required
def get_user_file(visited_user_email,file_name):
    try:
        subdir=visited_user_email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        public=os.path.join(user_folder, "public")
        return send_from_directory(public, path=file_name, as_attachment=True)
    except FileNotFoundError:
        return "File Not Fouund!", 404

#***************************
#***************************











#***********************************
# Add/remove friend from friendlist
#***********************************

@views.route("/friend")
@login_required
def get_friends():
    subdir=current_user.email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
    friends=os.path.join(user_folder, "friends")
    
    return render_template("friend.html",user=current_user,directory=user_folder,friends=os.listdir(friends))


@views.route("/search-user-friend/<string:visited_user_email>")
@login_required
def search_user_friend(visited_user_email):
    subdir=visited_user_email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)

    public=os.path.join(user_folder, "public")

    email=subdir
    user=User.query.filter_by(email=email).first()
    if user:
        subdir=email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        public=os.path.join(user_folder, "public")
        return render_template("visit_user.html",user=current_user,visited_user=user,directory=user_folder,files2=os.listdir(public),email=email)
    user=GoogleUser.query.filter_by(email=email).first()
    if user:
        subdir=email
        user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
        public=os.path.join(user_folder, "public")
        flash("User Found!",category="success")
        return render_template("visit_user.html",user=current_user,visited_user=user,directory=user_folder,files2=os.listdir(public),email=email)
    
    return render_template("home.html",user=current_user)    

@views.route('/register-friend/<string:visited_user_email>/<string:visited_user_name>')
@login_required
def register_friend(visited_user_email,visited_user_name):
    subdir_curr=current_user.email
    subdir_vis=visited_user_email
    user_folder_curr = os.path.join(app.config["FILE_UPLOADS"], subdir_curr)
    user_folder_vis = os.path.join(app.config["FILE_UPLOADS"], subdir_vis)

    friends = os.path.join(user_folder_curr,"friends")
    public=os.path.join(user_folder_vis, "public")

    friend=os.path.join(friends, visited_user_email+"_"+visited_user_name)
    if not os.path.isdir(friend):
        os.mkdir(friend)
    user=User.query.filter_by(email = visited_user_email).first()
    return render_template("visit_user.html",user=current_user,visited_user=user,email=visited_user_email,directory=user_folder_vis,files2=os.listdir(public),friendStat=1)

@views.route('/remove-friend/<string:visited_user_email>/<string:visited_user_name>')
@login_required
def remove_friend(visited_user_email,visited_user_name):
    subdir_curr=current_user.email
    subdir_vis=visited_user_email
    user_folder_curr = os.path.join(app.config["FILE_UPLOADS"], subdir_curr)
    user_folder_vis = os.path.join(app.config["FILE_UPLOADS"], subdir_vis)

    friends = os.path.join(user_folder_curr,"friends")
    public=os.path.join(user_folder_vis, "public")

    friend=os.path.join(friends, visited_user_email+"_"+visited_user_name)
    os.rmdir(friend)

    user=User.query.filter_by(email = visited_user_email).first()
    return render_template("visit_user.html",user=current_user,visited_user=user,email=visited_user_email,directory=user_folder_vis,files2=os.listdir(public),friendStat=-1)
    
@views.route('/remove-friend-html/<string:visited_user_email>/<string:visited_user_name>')
@login_required
def remove_friend_html(visited_user_email,visited_user_name):
    subdir_curr=current_user.email
    subdir_vis=visited_user_email
    user_folder_curr = os.path.join(app.config["FILE_UPLOADS"], subdir_curr)
    user_folder_vis = os.path.join(app.config["FILE_UPLOADS"], subdir_vis)

    friends = os.path.join(user_folder_curr,"friends")
    public=os.path.join(user_folder_vis, "public")

    friend=os.path.join(friends, visited_user_email+"_"+visited_user_name)
    os.rmdir(friend)

    user=User.query.filter_by(email = visited_user_email).first()
    return render_template("friend.html",user=current_user,directory=user_folder_curr,friends=os.listdir(friends))

#***************************
#***************************











#*****************************
# create a text file using editor
#*****************************


def remove_first_end_spaces(string):
    return "".join(string.rstrip().lstrip())

@views.route('/create-doc', methods=["GET","POST"])
@login_required
def create_doc():
    subdir=current_user.email
    user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
    public=os.path.join(user_folder, "public")
    private=os.path.join(user_folder, "private")
    
    if request.method=='POST':
        f=request.form.get('editordata')
        name=request.form.get('fileName')
        h = html2text.HTML2Text()
        h.ignore_links = False
        l=h.handle(f)
        l=remove_first_end_spaces(l)
        print(len(l),l,h.handle(f))

        if(len(l)==0 or len(name)==0):
            flash("Fields cannot be empty!!", category='error')
            return redirect(request.url)

        else:
            subdir=current_user.email
            user_folder = os.path.join(app.config["FILE_UPLOADS"], subdir)
            public=os.path.join(user_folder, "public")
            private=os.path.join(user_folder, "private")
            if request.form["directory"]=="public":
                directory=public
            else:
                directory=private
            filepath = os.path.join(directory, name+".txt")
            if(os.path.exists(filepath)):
                flash("filename already used!", category='error')
                return redirect(request.url)     
            try:
                with open(os.path.join(filepath), 'w') as f:
                    f.write(l)
                flash('file uploaded successfully!', category='success')
                f.close()
                return redirect(request.url)
            except FileNotFoundError:
                flash("The directory does not exist", category='error')    
                return redirect(request.url)

    return render_template("editor.html",user=current_user,directory=user_folder,files1=os.listdir(private),files2=os.listdir(public))      


# **************************** 
# ****************************   