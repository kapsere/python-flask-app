from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_assets import Environment
from bundles import bundles
from flask_jsglue import JSGlue
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_msearch import Search

#create the application object
app = Flask(__name__)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message_category = "info"
assets = Environment(app)
assets.register(bundles)
jsglue = JSGlue(app)

#importing config.py
import os
app.config.from_object(os.environ['APP_SETTINGS'])

# create the SQLAlchemy object
db = SQLAlchemy(app)
mail = Mail(app)

#flask-moment
moment = Moment(app)

#Flask-CKEditor

ckeditor = CKEditor(app)

#Flask-msearch
search = Search()
search.init_app(app)
""" if you already have posts in your db, use the following code to index them
#importing the db model
from project.models import BlogPost
#create searchable index of the model
search.create_index(BlogPost)"""

#Blueprints
from project.users.views import users_blueprint
from project.home.views import home_blueprint
from project.blog.views import blog_blueprint

#register blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(blog_blueprint)

#Flask-Login
#defining login view
from project.models import User

login_manager.login_view = "users.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
    
########################
#### error handlers ####
########################

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('errors/413.html'), 413
    
@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500    
    
