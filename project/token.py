from itsdangerous import URLSafeTimedSerializer

from project import app

#confirm account token
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email
     
#reset account password token
def generate_reset_token(email):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return password_reset_serializer.dumps(email, salt=app.config['PASSWORD_RESET_SALT'])
    
def reset_token(token, expiration=3600):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = password_reset_serializer.loads(
            token, 
            salt=app.config['PASSWORD_RESET_SALT'], 
            max_age=expiration
            )
    except:
        return False
    return email    
    