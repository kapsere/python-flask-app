from project import db
from flask import render_template, Blueprint, redirect, url_for
from flask_login import current_user


################
#### config ####
################

home_blueprint = Blueprint(
    'home', __name__,
    template_folder='templates'
)

# use decorators to link the function
@home_blueprint.route('/')
def home():
    return render_template("index.html")