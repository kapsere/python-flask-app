from project import db, bcrypt
import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class BlogPost(db.Model):
    
    __searchable__ = ['title', 'content']
    
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String, unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, nullable=True, index=True)
    comments = db.relationship('Comments', backref='postid', foreign_keys="[Comments.post_id]")
    comments_post_title = db.relationship('Comments', backref="posttitle",foreign_keys="[Comments.comment_post_title]", lazy="dynamic")
    

    def __init__(self, title, content, slug, author_id, timestamp):
        self.title = title
        self.content = content
        self.slug = slug
        self.author_id = author_id
        self.timestamp = timestamp 
    
    def __repr__(self):
        return 'Post: {}'.format(self.title)
        
class Comments(db.Model): 
    
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    comment_content = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    comment_post_title = db.Column(db.String, db.ForeignKey('posts.slug'))
    comment_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    
    def __init__(self, comment_content, timestamp, post_id, comment_post_title, comment_user_id):
        self.comment_content = comment_content
        self.timestamp = timestamp
        self.post_id = post_id
        self.comment_post_title = comment_post_title
        self.comment_user_id = comment_user_id
    
    def __repr__(self):
        return '<comment {}'.format(self.comment_content)
 

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    about = db.Column(db.String(300), default=None, nullable=True)
    image_url = db.Column(db.String, default=None, nullable=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String, default=None, nullable=True)
    posts = db.relationship('BlogPost', backref='author', lazy='dynamic')
    comments = db.relationship('Comments', backref='comment_author', lazy='dynamic')
    followed = db.relationship('User', 
                                secondary=followers, 
                                primaryjoin=(followers.c.follower_id == id), 
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic')
    

    def __init__(self, name, email, password, confirmed, role, admin, confirmed_on=None, about=None, last_seen=None, image_url=None ):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8') 
        self.registered_on= datetime.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.last_seen = last_seen
        self.image_url = image_url
        self.admin = admin
        self.role = role
        self.about = about
        
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return '{}'.format(self.name)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0