from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField , TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from project.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired

#Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
#Enable User Registration
class RegisterForm(FlaskForm):
    username = StringField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = StringField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=40)]
    )
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(), EqualTo('password', message='Passwords must match.')
        ]
    )
    
#Profile Page Change Password    
class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    
#Profile Page Personal Info
class ProfileInfoForm(FlaskForm):
    about_user = TextAreaField('About Me')
    name = StringField('username',validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('email', validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    
#Profile page upload picture
class UploadForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[FileRequired()])    
    
#Password reset via email        
class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=40)])
class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

