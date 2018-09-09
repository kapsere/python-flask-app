import os
basedir = os.path.abspath(os.path.dirname(__file__))
# default config
class BaseConfig(object):
    DEBUG = False
    """ Generate secret & salts using os.urandom() """
    SECRET_KEY = 'yoursecretkey'
    SECURITY_PASSWORD_SALT = 'yoursalt'
    PASSWORD_RESET_SALT = 'yoursalt'
    SQLALCHEMY_DATABASE_URI = os.environ['APP_DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
  
    #Flask-mail settings
    MAIL_SERVER = os.environ['APP_MAIL_SERVER']
    MAIL_PORT = os.environ['APP_MAIL_PORT']
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    #Flaks-mail auth
    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']
    #Flask-mail accounts 
    MAIL_DEFAULT_SENDER = os.environ['APP_MAIL_USERNAME']
    
    #Flask-CKEditor
    CKEDITOR_FILE_UPLOADER = '/blog/upload' #name of your view route
    CKEDITOR_SERVE_LOCAL = True
    CK_UPLOAD_PATH = os.environ['APP_CK_UPLOAD_PATH']
    CKEDITOR_EXTRA_PLUGINS=['imagebrowser']
    #Flask-msearch
    MSEARCH_INDEX_NAME = 'whoosh_index'
    #setting backend to whoosh
    MSEARCH_BACKEND = 'whoosh'
    #auto create or update index
    MSEARCH_ENABLE = True
    
    #File uploads
    UPLOAD_FOLDER = os.environ['APP_FILE_UPLOADS_FOLDER']
    ALLOWED_EXTENSIONS = set(['jpg', 'gif', 'png', 'jpeg'])
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    UPLOADS_URL = os.environ['APP_FILE_UPLOADS_URL']

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TEST_IMG_PATH = os.environ['APP_TEST_IMG_PATH']

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    MAIL_DEBUG = True
    
class ProductionConfig(BaseConfig):
    DEBUG = False