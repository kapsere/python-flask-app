from flask import flash, redirect, render_template, request, \
    url_for, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
from .form import LoginForm, RegisterForm, ChangePasswordForm, EmailForm, PasswordForm,ProfileInfoForm,UploadForm
from project import db,app
from project.models import User, bcrypt, BlogPost, Comments
from project.token import generate_confirmation_token, confirm_token, generate_reset_token, reset_token
import datetime
from project.email import send_email
from project.decorators import check_confirmed
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, DataError
from werkzeug.utils import secure_filename    
import os
from PIL import Image


users_blueprint = Blueprint(
    'users', __name__ ,
    template_folder='templates'
) 
#User Login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        return redirect (url_for('blog.home'))
    if request.method == 'POST':   
        if form.validate_on_submit(): 
            user = User.query.filter_by(email=request.form['email']).first()
            if user is not None and bcrypt.check_password_hash(
                user.password, request.form['password']):
                    
                
                login_user(user)
                user.last_seen = datetime.datetime.now()
                db.session.commit()
                return redirect(url_for('blog.home'))
            else:
                error = flash('There was a problem with your login.','danger')
    return render_template('login.html', form=form, error=error)
    
#User Logout 
@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.', 'success')
    return redirect(url_for('users.login'))
    
#User Account Registration    
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect (url_for('users.unconfirmed'))
    if current_user.is_authenticated and current_user.confirmed:
        return redirect (url_for('blog.home'))
    form = RegisterForm()
    try :
        if form.validate_on_submit():
            user = User(
                name=form.username.data,
                email=form.email.data,
                password=form.password.data,
                admin=False,
                confirmed=False,
                role="user"
            )
            db.session.add(user)
            db.session.commit()
            
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('users.confirm_email', token=token, _external=True)
            html = render_template('emails/email_activation.html', confirm_url=confirm_url)
            subject = "Please confirm your account"
            send_email(user.email, subject, html)
    
            login_user(user)
            return redirect(url_for('blog.home'))
    except IntegrityError : 
            db.session.rollback()
            flash('Email and/or Username already in use', 'danger')        
    return render_template('register.html', form=form)
    
#User Account Confirmation     
@users_blueprint.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash('Account already confirmed.', 'success')
        return redirect(url_for('blog.home'))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('blog.home'))
    
#Resend User Account Confirmation Email Link
@users_blueprint.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('users.confirm_email', token=token, _external=True)
    html = render_template('emails/email_activation.html', confirm_url=confirm_url)
    subject = "Please confirm your account"
    send_email(current_user.email, subject, html)
    return redirect(url_for('users.unconfirmed')) 
    
#Unconfirmed User Account Page    
@users_blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('blog.home'))
    
    return render_template('account_unconfirmed.html')
    
#################
#### PROFILE ####
#################
#User Profile Page
@users_blueprint.route('/profile/<username>')
@login_required
@check_confirmed
def profile(username):
    user = User.query.filter_by(name=username).first_or_404()
    posts = BlogPost.query.filter_by(author_id=user.id).order_by(desc(BlogPost.timestamp)).limit(5).all()
    comments = Comments.query.filter_by(comment_user_id=user.id).order_by(desc(Comments.timestamp)).limit(5).all()
    return render_template('profile.html' , user=user, posts=posts, comments=comments)

#User Profile Settings Page   
@users_blueprint.route('/profile_settings')
@login_required
@check_confirmed
def profile_settings():
    profile_info_form = ProfileInfoForm(request.form)
    profile_picture_form = UploadForm() 
    return render_template('profile_settings.html', profile_info_form=profile_info_form, profile_picture_form=profile_picture_form)  
    
#User Profile Change/Update Settings
@users_blueprint.route('/update_settings', methods=['POST'])
@login_required
@check_confirmed
def update_settings():
    profile_info_form = ProfileInfoForm(request.form)
    profile_picture_form = UploadForm() 
    try :
        if profile_info_form.validate_on_submit():
            user = User.query.filter_by(email=current_user.email).first()
            if user:
                user.about = profile_info_form.about_user.data
                user.email = profile_info_form.email.data
                user.name = profile_info_form.name.data
                db.session.commit()
                flash('Info Updated.','success')
                return redirect(url_for('users.profile_settings'))
    except IntegrityError : 
            db.session.rollback()
            flash('Email and/or Username already in use. Profile not updated', 'danger')              
            return redirect(url_for('users.profile_settings'))
    except DataError : 
            db.session.rollback()
            flash('Your "about" text was too long. Character limit is 150.', 'danger')              
            return redirect(url_for('users.profile_settings'))        
    return render_template('profile_settings.html', profile_info_form=profile_info_form, profile_picture_form=profile_picture_form)  
    
#Allowed Files For Upload
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS'] 
        
#Optimize images with Pillow
def compress_image(filename,filepath,fext):
    #Open the saved image
    img = Image.open(filename)
    #Resize the image
    size = (350, 350)
    img.thumbnail(size,Image.ANTIALIAS)
    #Compress the image
    img.save('{}{}'.format(filepath,fext),quality=65,optimize=True)

#User File Upload Profile Picture   
@users_blueprint.route('/upload', methods=['POST']) 
@login_required
@check_confirmed
def add_profilepicture():
    profile_info_form = ProfileInfoForm(request.form)
    profile_picture_form = UploadForm()
    if request.method == 'POST' and 'picture' in request.files:
        if profile_picture_form.validate_on_submit():
            user = User.query.filter_by(name=current_user.name).first()
            f = request.files.get('picture')
            #splitting the filename and the extension
            file_name,fext = os.path.splitext(f.filename)
            #changing filename to profile-picture
            #file_name = secure_filename('profile-picture' "%s" % (fext))
            file_name = secure_filename('profile-picture')
            #Creating a path 
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],str(user),file_name)
            #Turning it into a dir
            dirname = os.path.dirname(filepath)
            # if the file extension is not allowed flash error
            if not allowed_file(f.filename):
                flash('Images only. Filetype not allowed.', 'danger')
                return redirect(url_for('users.profile_settings'))
            # if the directory does not exist    
            elif not os.path.exists(dirname):
                try:    
                    # create the dir
                    os.makedirs(dirname)
                    # save the file
                    if fext == '.png' or fext == '.JPG' or fext == '.PNG':
                        fext = '.jpg'
                        f.save('{}{}'.format(filepath,fext))
                        file_name = secure_filename('profile-picture.jpg')
                        user.image_url = os.path.join(app.config['UPLOADS_URL'],str(user),file_name)
                        db.session.add(user)
                        db.session.commit()
                        compress_image(f,filepath,fext)
                        flash('Profile picture added.','success')
                    else : 
                        f.save('{}{}'.format(filepath,fext))
                        user.image_url = os.path.join(app.config['UPLOADS_URL'],str(user),file_name+fext)
                        db.session.add(user)
                        db.session.commit()
                        compress_image(f,filepath,fext)
                        flash('Profile picture added.','success')
                    return redirect(url_for('users.profile_settings'))    
                except:
                    flash("can't create directory.",'danger')
                    return redirect(url_for('users.profile_settings'))
            elif not os.access(dirname,os.W_OK):
                flash("can't write to directory.",'danger')
                return redirect(url_for('users.profile_settings'))
            elif fext == '.png' or fext == '.JPG' or fext == '.PNG':
                fext = '.jpg'
                f.save('{}{}'.format(filepath,fext))
                file_name = secure_filename('profile-picture.jpg')
                user.image_url = os.path.join(app.config['UPLOADS_URL'],str(user),file_name)
                db.session.add(user)
                db.session.commit()
                compress_image(f,filepath,fext)
                flash('Profile picture added.','success')
                return redirect(url_for('users.profile_settings')) 
            else : 
                f.save('{}{}'.format(filepath,fext))
                user.image_url = os.path.join(app.config['UPLOADS_URL'],str(user),file_name+fext)
                db.session.add(user)
                db.session.commit()
                compress_image(f,filepath,fext)
                flash('Profile picture added.','success')
            return redirect(url_for('users.profile_settings'))
    return render_template('profile_settings.html', profile_info_form=profile_info_form, profile_picture_form=profile_picture_form) 

#Profile Password Change 
@users_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
@check_confirmed
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            #.decode('utf-8') fixed bcrypt invalid salt error in Python 3
            #https://github.com/maxcountryman/flask-bcrypt/issues/36
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash('Password successfully changed.','success')
            return redirect(url_for('users.change_password'))
        else:
            flash('Password change was unsuccessful.','danger')
            return redirect(url_for('users.change_password'))
    return render_template('profile_password_settings.html', form=form)
   
#User Password Reset via Email    
@users_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first_or_404()
        except:
            flash('Invalid email address', 'danger')
            return render_template('password_reset.html', form=form)
         
        if user.confirmed:
            token = generate_reset_token(user.email)
            password_reset_url = url_for('users.reset_with_token', token=token, _external=True)
            html = render_template('emails/email_password_reset.html', password_reset_url=password_reset_url)
            subject = "Password Reset Requested"
            send_email(user.email, subject, html)
            flash('Please check your email for a password reset link.', 'success')
        else:
            flash('Your email address must be confirmed before attempting a password reset.', 'danger')
        return redirect(url_for('users.login'))
 
    return render_template('password_reset.html', form=form)
 
@users_blueprint.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = reset_token(token)
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('users.login'))
 
    form = PasswordForm()
 
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first_or_404()
        except:
            flash('Invalid email address', 'danger')
            return redirect(url_for('users.login'))
        #.decode('utf-8') fixed bcrypt invalid salt error in Python 3
        #https://github.com/maxcountryman/flask-bcrypt/issues/36
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.add(user)
        db.session.commit()
        flash('Password sucessfully changed', 'success')
        return redirect(url_for('users.login'))
 
    return render_template('password_reset_with_token.html', form=form, token=token)

######################
#FOLLOW/UNFOLLOW USER#
######################
@users_blueprint.route('/follow/<username>')
@login_required
@check_confirmed
def follow(username):
    user = User.query.filter_by(name=username).first_or_404()
    if user == current_user:
        return redirect(url_for('users.profile', username=username))
    u = current_user.follow(user)
    if u is None:
        return redirect(url_for('users.profile', username=username))
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('users.profile', username=username))

@users_blueprint.route('/unfollow/<username>')
@login_required
@check_confirmed
def unfollow(username):
    user = User.query.filter_by(name=username).first_or_404()
    if user == current_user:
        return redirect(url_for('users.profile', username=username))
    u = current_user.unfollow(user)
    if u is None:
        return redirect(url_for('users.profile', username=username))
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('users.profile', username=username))