import unittest
import datetime
from flask_testing import TestCase
from flask_login import current_user
from project import app, db
from project.models import User, BlogPost, Comments
from project.users.form import RegisterForm, ChangePasswordForm, UploadForm
from project.blog.form import CommentForm, SearchForm,CKEditorForm
from project.token import generate_confirmation_token, confirm_token
from io import BytesIO

class BaseTestCase(TestCase):
    """A base test case."""
    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.add(Comments('This is a test comment', timestamp=datetime.datetime.utcnow(), post_id=1, comment_user_id=1, comment_post_title="test"))
        db.session.add(User("admin", "admin@test.com", "administrator",admin=True, role="admin", confirmed=True))
        db.session.add(User("jane","jane@test.com", "123456", admin=True, role="admin", confirmed=False))
        db.session.add(User("peter","peter@test.com", "456789", admin=False, role="user", confirmed=True))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    ###Helper methods### 
    def login(self):
        return self.client.post(
            '/login',
            data=dict(email="admin@test.com", password="administrator"),
            follow_redirects=True
        )
    def add_post(self):
       db.session.add(BlogPost("Test post", "This is a test. Only a test.", timestamp=datetime.datetime.utcnow(),author_id=1, slug="test")) 
       db.session.commit()


        
class FlaskTestCase(BaseTestCase):
    #Test if flask was set up correctly
    def test_index(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
class UserViewsTests(BaseTestCase):  
    
    #Test that login loads correctly
    def test_login_page_loads(self):
        response = self.client.get('/login', content_type='html/text')
        self.assertTrue(b'Log in' in response.data)
        
    #Test login behaves correctly given the correct credentials 
    def test_correct_login(self):
        with self.client:
            self.login()
            self.assertTrue(current_user.name == 'admin')
            self.assertTrue(current_user.email == "admin@test.com")
            self.assertTrue(current_user.is_active())
            self.assertTrue(current_user.is_authenticated()) 
    
    #Test login behaves correctly given the incorrect credentials / Ensure invalid email format throws error
    def test_incorrect_login(self):
        response =self.client.post(
            '/login', 
            data=dict(email="wrong", password="administrator"), 
            follow_redirects = True)
        self.assertTrue(response.status_code == 200)
        self.assertIn(b'There was a problem with your login.', response.data)
        
    #Test the logout behaves correctly    
    def test_logout(self):
        with self.client:
            response = self.client.post('/login', data=dict(email="admin@test.com", password="administrator"), follow_redirects = True)
            response = self.client.get('/logout', follow_redirects = True)
            self.assertIn(b'You were logged out.', response.data) 
            
    #Test users can register
    def test_user_registration(self):
        with self.client:
            response = self.client.post('/register', data=dict(username="rhonda", email="rhonda@test.com", password="123456", confirm="123456"), follow_redirects = True)
            self.assertTrue(current_user.name == 'rhonda')
            self.assertTrue(current_user.email == "rhonda@test.com")
            self.assertTrue(current_user.is_active())
            self.assertTrue(current_user.is_authenticated())  
            
    #Testing Confirm Token
    
    #Test user can confirm account with valid token.    
    def test_confirm_token_route_valid_token(self):
        with self.client:
            self.client.post('/login', data=dict(
                email='jane@test.com', password='123456'
            ), follow_redirects=True)
            token = generate_confirmation_token('jane@test.com')
            response = self.client.get('/confirm/'+token, follow_redirects=True)
            self.assertIn(b'You have confirmed your account. Thanks!', response.data)
            user = User.query.filter_by(email='jane@test.com').first_or_404()
            self.assertIsInstance(user.confirmed_on, datetime.datetime)
            self.assertTrue(user.confirmed)
    
    #Test user cannot confirm account with invalid token. 
    def test_confirm_token_route_invalid_token(self):
        token = generate_confirmation_token('jane@test1.com')
        with self.client:
            self.client.post('/login', data=dict(
                email='jane@test.com', password='123456'
            ), follow_redirects=True)
        response = self.client.get('/confirm/'+token, follow_redirects=True)
        self.assertIn(
            b'The confirmation link is invalid or has expired.',
            response.data
        )    
    #Test user cannot confirm account with expired token.
    def test_confirm_token_route_expired_token(self):
        user = User(name='test', email='test@test.com',admin=False, password='testing', role="admin", confirmed=False)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token('test@test.com')
        self.assertFalse(confirm_token(token, -1))
        
    #Test User follow/unfollow functionality
    def test_follow(self):
        u1 = User('john', 'john@test.com','testing123', admin=True, role="admin", confirmed=True)
        u2 = User('susan','susan@test.com','testing123', admin=True, role="admin", confirmed=True)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().name == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().name == 'john'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    #User Upload image test
    def test_image_upload(self):
        self.login()
        
        with open(app.config['TEST_IMG_PATH'],'rb') as img1:
            imgBytesIO1 = BytesIO(img1.read())
            
        response = self.client.post('/upload',content_type='multipart/form-data',
                                    data={'image':(imgBytesIO1, 'img1.jpg')},
                                    follow_redirects=True)
        self.assertEqual(response.status,"200 OK")
        
    ###TEST ROUTE REQUIRES LOGIN###
    
    #Test confirm/<token> route requires logged in user.
    def test_confirm_token_route_requires_login(self):
        response = self.client.get('/confirm/blah', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    
    #Test user unconfirmed route requires login
    def test_user_unconfirmed_route_requires_login(self):
        response = self.client.get('/unconfirmed',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    
    #Test resend confirmation link route requires login
    def test_user_resend_confirmation_route_requires_login(self):
        response = self.client.get('/resend',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)    
    
    #Test logout page requires login
    def test_logout_route_requires_login(self):
        response = self.client.get('/logout', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    
    #Test Profile Page requires login
    def test_profile_route_requires_login(self):
        response = self.client.get('/profile/jane', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)    
        
    #Test Profile Settings Page requires login
    def test_profile_settings_route_requires_login(self):
        response = self.client.get('/profile_settings', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
        
    #Test Profile Settings Update requires login
    def test_profile_settings_update_route_requires_login(self):
        response = self.client.post('/update_settings', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)    
        
    #Test Profile Settings Picture add requires login
    def test_profile_settings_picture_add_route_requires_login(self):
        response = self.client.post('/upload', follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)  
        
    #Test Profile Settings change password requires login    
    def test_profile_settings_change_password_route_requires_login(self):
        response = self.client.get('/change_password',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)  
        
    #Test user follow route requires login
    def test_user_follow_route_requires_login(self):
        response = self.client.get('/follow/jane',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
        
    #Test user unfollow route requires login
    def test_user_unfollow_route_requires_login(self):
        response = self.client.get('/unfollow/jane',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    
    
        
    ###FORM VALIDATION###
    
    #Test correct register data validates
    def test_validate_success_register_form(self):
        form = RegisterForm(
            username="jane", 
            email="test@test.com", 
            password="123456",
            confirm="123456"
            )
        self.assertTrue(form.validate())
        
    #Test incorrect register data does not validate.    
    def test_validate_invalid_password_format(self):
        form = RegisterForm(
            username ='admin',
            email='admin@test.com',
            password='example', 
            confirm='crap')
        self.assertFalse(form.validate())
    
    #Test user can't register when a duplicate email is used 
    def test_validate_email_already_registered(self):
        response = self.client.post('/register', data=dict(username='admin',email='admin@test.com',password='administrator',confirm='administrator',follow_redirects=True))
        self.assertIn(b'Email and/or Username already in use', response.data)
    #Test user can't register when a duplicate username is used
    def test_validate_username_already_registered(self):
        response = self.client.post('/register', data=dict(username='admin',email='testing@users.com',password='administrator',confirm='administrator',follow_redirects=True))
        self.assertIn(b'Email and/or Username already in use', response.data)    
        
    #Profile Page Change PasswordForm Tests
    
    #Test correct password data validates.
    def test_validate_success_change_password_form(self):
        form = ChangePasswordForm(password='update', confirm='update')
        self.assertTrue(form.validate())
        
    #Test passwords must match.
    def test_validate_invalid_change_password(self):
        form = ChangePasswordForm(password='update', confirm='unknown')
        self.assertFalse(form.validate())
        
    #Test invalid password format throws error. Password should be atleast 6 characters and at the most 25 characters long
    #Testing if password that is too long/short throws error
    def test_validate_invalid_change_password_format(self):
        form = ChangePasswordForm(password='123456789123456789123456789', confirm='123456789123456789123456789')
        self.assertFalse(form.validate())
        
#######################        
### BLOG VIEW TESTS ###
#######################
class BlogViewsTests(BaseTestCase):    
    #Test posts show up on the blog index page
    def test_posts_show_up(self):
        self.add_post()
        response = self.login()
        self.assertTrue(b'This is a test. Only a test.' in response.data)
        
    #Test comments show up on the blog post page
    def test_comments_show_up(self):
        self.login()
        self.add_post()
        response = self.client.get('/blog/test/')
        self.assertTrue(b'This is a test comment' in response.data)
    
    #Test posts can be added
    def test_post_add(self):
        post = BlogPost("Another test", "adding another test", timestamp=datetime.datetime.utcnow(),author_id=1, slug="Another test")
        db.session.add(post)
        db.session.commit()
        self.login()
        response = self.client.get('/blog')
        self.assertIn(b'Another test',response.data)
        
    #Test posts can be deleted
    def test_post_delete(self):
        self.add_post()
        self.login()
        response = self.client.post('/blog/delete/test/',follow_redirects = True)
        self.assertIn(b'Post Deleted.', response.data)    
        
    #Test comment can be added
    def test_comment_add(self):
        self.add_post()
        self.login()
        response = self.client.post('blog/test/add_comment',data=dict(comment="testing comment add."),follow_redirects = True)
        self.assertIn(b'testing comment add.', response.data)
        
    #Test comments can be deleted
    def test_comment_delete(self):
        self.add_post()
        self.login()
        response = self.client.post('/blog/test/delete_comment/1',follow_redirects = True)
        self.assertIn(b'Comment Deleted.', response.data)
    
    #Search for posts test
    def test_search_post(self):
        post1 = self.add_post()
        results = BlogPost.query.msearch('test').all()
        self.assertEqual(len(results), 1)
    
    ###TEST ROUTE REQUIRES LOGIN###
    #blog index 
    def test_blog_route_requires_login(self):
        response = self.client.get('/blog',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    #blog individual post
    def test_blog_post_route_requires_login(self):
        response = self.client.get('/blog/test',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    #add blog post
    def test_add_blog_post_route_requires_login(self):
        response = self.client.get('/blog/add_blog_post',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    #delete blog post
    def test_delete_blog_post_route_requires_login(self):
        response = self.client.post('/blog/delete/test/',follow_redirects = True)
        self.assertIn(b'Please log in to access this page.',response.data)
    #add comment to post
    def test_add_comment_route_requires_login(self):
        response = self.client.post('/blog/test/add_comment',follow_redirects = True)
        self.assertIn(b'Please log in to access this page.',response.data)
    #delete comment from post
    def test_delete_comment_route_requires_login(self):
        response = self.client.post('/blog/test/delete_comment/1',follow_redirects = True)
        self.assertIn(b'Please log in to access this page.',response.data)
    #search route
    def test_search_route_requires_login(self):
        response = self.client.post('/blog/search',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    #ckupload route
    def test_ckupload_route_requires_login(self):
        response = self.client.post('/blog/upload',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
    #ckupload files route    
    def test_ckupload_files_requires_login(self):   
        response = self.client.get('/blog/files',follow_redirects = True)
        self.assertTrue(b'Please log in to access this page.' in response.data)
        
    ###TEST ROUTE REQUIRES ADMIN###
    #add blog post
    def test_add_blog_post_requires_admin(self):
        login = self.client.post('/login',data=dict(email="peter@test.com", password="456789",follow_redirects = True))
        response = self.client.get('/blog/add_blog_post',follow_redirects = True)
        self.assertFalse(b'What is on your mind' in response.data)
    #delete blog post
    def test_delete_blog_post_requires_admin(self):
        login = self.client.post('/login',data=dict(email="peter@test.com", password="456789",follow_redirects=True))
        response = self.client.post('/blog/delete/test/',follow_redirects = True)
        self.assertFalse(b'Post Deleted.' in response.data)
    #delete comment in post
    def test_delete_comment_requires_admin(self):
        login = self.client.post('/login',data=dict(email="peter@test.com", password="456789",follow_redirects = True))
        response = self.client.post('/blog/test/delete_comment/1',follow_redirects = True)
        self.assertFalse(b'Comment Deleted.' in response.data)
    #ckupload route
    def test_ckupload_route_requires_admin(self):
        login = self.client.post('/login',data=dict(email="peter@test.com", password="456789",follow_redirects = True))
        response = self.client.post('/blog/upload',follow_redirects = True)
        self.assertIn(b'blog', response.data)
    #ckupload files route    
    def test_ckupload_files_requires_admin(self):   
        login = self.client.post('/login',data=dict(email="peter@test.com", password="456789",follow_redirects = True))
        response = self.client.get('/blog/files',follow_redirects = True)
        self.assertIn(b'blog', response.data)
        
    ###FORM VALIDATION###  
    
    #Test Post form validation 
    def test_post_validate_form(self):
        form = CKEditorForm(title="this is post form validation test",content="blablabla")
        self.assertTrue(form.validate())
        
    #Test comment form validation 
    def test_comment_validate_form(self):
        form = CommentForm(comment="test comment add form validation")
        self.assertTrue(form.validate())
    
    #Test post search form validation
    def test_posts_search_validate_form(self):
        form = SearchForm(search="test")
        self.assertTrue(form.validate())    
            
        
if __name__ == '__main__':
    unittest.main()