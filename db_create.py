from project import db
from project.models import BlogPost,User,Comments

#create the database and the db tables
db.create_all()

#commit the changes
db.session.commit()