from threading import Thread
from flask_mail import Message
from project import app, mail
from project.decorators import async
import os
@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=(os.environ['APP_EMAIL_SENDER_NAME'],os.environ['APP_EMAIL_SENDER_ADDRESS'] )
    )
    send_async_email(app, msg)
