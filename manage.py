from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime
import os

from project import app, db
from project.models import User

app.config.from_object(os.environ['APP_SETTINGS'])
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def create_admin():
    print('Creating Admin')
    """Creates the admin user."""
    db.session.add(User(
        email="admin@test.com",
        name="Administrator",
        password="administrator",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        role="admin")
    )
    db.session.commit()
    
@manager.command    
def create_user():   
    print('Creating User')
    """ Creates a regular user."""
    db.session.add(User(
        email="testuser@test.com",
        name="User",
        password="testuser",
        admin=True,
        confirmed=True,
        confirmed_on=datetime.datetime.now(),
        role="user")
    )
    db.session.commit()


if __name__ == '__main__':
    manager.run()