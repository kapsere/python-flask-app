from functools import wraps
from threading import Thread
from flask import flash, redirect, url_for
from flask_login import current_user

#function for threading 
def async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
        
    return wrapper
    
#check if user.confirmed=true
def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            return redirect(url_for('users.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
    

#check if user.admin=true
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.admin is False :
            return redirect(url_for('blog.home'))
        return func(*args, **kwargs) 
    
    return decorated_function