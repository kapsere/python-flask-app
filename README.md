# Flask app
Blogging/social app. 
##### Some Features
* User registration
* User profiles 
	* User uploads
   * Follow/unfollow users  
  * See users recent activity
	  * Recent posts
	  * Recent comments
* WYSIWYG editor(CKEditor)
  * file uploads
  * file browser 
* Post comment system
* User roles 
* Image compression for uploads using Pillow
* Email for account confirmation/password reset

### Environment variables
|Environment variable name  | Description  |
|--|--|
|APP_DATABASE_URL|The URL of your database.|
|APP_MAIL_SERVER|The address of your mail relay server.|
|APP_MAIL_PORT|The port of your mail relay server.|
|APP_MAIL_USERNAME|The username of your mail relay server account.|
|APP_MAIL_PASSWORD|Password of your mail relay server account.|
|APP_CK_UPLOAD_PATH|Ckeditor upload destination path.|
|APP_FILE_UPLOADS_FOLDER|User file uploads destination path.|
|APP_FILE_UPLOADS_URL|The URL of your file uploads path.|
|APP_EMAIL_SENDER_NAME|The name used for sending emails.|
|APP_EMAIL_SENDER_ADDRESS|The email address used for sending emails.|
|APP_TEST_IMG_PATH|Used for unit testing file uploads. |

### Install dependencies

> pip install -r requirements.txt

### Create the database

> python create_db.py

### Create an admin user

> python manage.py create_admin

### Create a regular user

> python manage.py create_user

### Start the app

> python manage.py runserver

#### CKEditor file browser config
> In *project/static/ckeditor/config.js*  
> Set config.imageBrowser_listUrl = "http://YourIpAddressOrWebsiteName/blog/files";

### TODO
- [ ] Update docs
- [ ] Implement JWT 
- [ ] Need better filebrowser implementation



app tested with python 2.7/3.5