from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
#Search the blog form
class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
#Post Comment form
class CommentForm(FlaskForm):
    comment = StringField('comment', validators=[DataRequired()])
#Flask-CKEditor form
class CKEditorForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    content = CKEditorField('content', validators=[DataRequired()])    
    submit = SubmitField('Post')
    
