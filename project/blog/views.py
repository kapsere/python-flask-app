from flask import flash, redirect, render_template, request, \
    url_for, Blueprint, abort, make_response,jsonify, send_from_directory
from flask_login import login_required, current_user
from .form import  SearchForm, CommentForm, CKEditorForm
from project import db,app
from project.models import User, BlogPost, Comments
import datetime
from project.decorators import check_confirmed, admin_required
from sqlalchemy import desc
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import os
import random
from flask_ckeditor import upload_success, upload_fail
from PIL import Image 

blog_blueprint = Blueprint(
    'blog', __name__ ,
    template_folder='templates'
) 

def global_map():
    recent_posts= db.session.query(BlogPost).order_by(desc(BlogPost.timestamp)).limit(5).all()
    form = SearchForm()
    map = {
         'recent_posts': recent_posts,
         'form' : form,
    }
    return map

#The Blog/Private Part Of The Site     
@blog_blueprint.route('/blog')
@blog_blueprint.route('/blog/<int:page>')
@login_required
@check_confirmed
def home(page=1):
    posts = db.session.query(BlogPost).order_by(desc(BlogPost.timestamp)).paginate(page,5, True)
    return render_template("blog.html", posts=posts, **global_map())
    
#Add Blog Post Page
@blog_blueprint.route('/blog/add_blog_post',  methods=['GET', 'POST'])
@login_required
@check_confirmed
@admin_required
def add_post():
    form = CKEditorForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(name=current_user.name).first()
            post = BlogPost(
                title = form.title.data, 
                content = form.content.data,
                slug = slugify(form.title.data),
                author_id = user.id, 
                timestamp = datetime.datetime.utcnow()
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog.home'))
        except IntegrityError : 
            db.session.rollback()
            flash('Post title must be unique. Please enter a new title.', 'danger')
    return render_template("add_blog_post.html", form=form)
    
#Link to individual Blog Posts    
@blog_blueprint.route('/blog/<slug>/')
@login_required
@check_confirmed
def post_detail(slug):
    try:
        post = db.session.query(BlogPost).filter_by(slug=slug).one()
    except NoResultFound :
        abort(404)
    return render_template('blog_post_detail.html', post=post, **global_map())
    
#Search Blog Posts
@blog_blueprint.route('/blog/search', methods=['POST'])
@login_required
@check_confirmed
def search():
    form = SearchForm()
    query = form.search.data
    if form.validate_on_submit():
        posts = BlogPost.query.msearch(query).all()
        return render_template("search_results.html", query=query, posts=posts, **global_map())
    else:
        return redirect(url_for('blog.home'))
        
#Add Comment
@blog_blueprint.route('/blog/<slug>/add_comment', methods=['POST'])
@login_required
@check_confirmed
def add_comment(slug):
    form = CommentForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=current_user.name).first()
        post = db.session.query(BlogPost).filter_by(slug=slug).one()
        comment = Comments(
                comment_content = form.comment.data,
                post_id = post.id, 
                comment_post_title = post.slug,
                comment_user_id = user.id,
                timestamp = datetime.datetime.utcnow()
            )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('blog.post_detail', slug=slug))
    else:
        flash('Comment field cannot be empty. Please Try again', 'info')
        return redirect(url_for('blog.post_detail', slug=slug))
        
#Delete Comment 
@blog_blueprint.route('/blog/<slug>/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
@check_confirmed
@admin_required
def delete_comment(slug, comment_id):
    comment = Comments.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment Deleted.','info')
    return redirect(url_for('blog.post_detail', slug=slug))
    
## Load more comments
@blog_blueprint.route('/<slug>/load_comments', methods=["POST"])
@login_required
@check_confirmed
def load_comments(slug):
    post = db.session.query(BlogPost).filter_by(slug=slug).one()
    return jsonify({'data' : render_template('comments.html',  post=post)})    
   
    
#Delete Blog Post & comments
@blog_blueprint.route('/blog/delete/<slug>/', methods=['POST'])
@login_required
@check_confirmed
@admin_required
def delete_post(slug):
    post= db.session.query(BlogPost).filter_by(slug=slug).one()
    for comment in post.comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash('Post Deleted.', 'info')
    return redirect(url_for('blog.home'))



#Flask-Ckeditor
@blog_blueprint.route('/files/<path:filename>')
@login_required
@check_confirmed
def uploaded_files(filename):
    path = app.config['CK_UPLOAD_PATH']
    return send_from_directory(path, filename)
    
#
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

    
@blog_blueprint.route('/blog/upload', methods=['POST'])
@login_required
@check_confirmed
@admin_required
def upload():
    error = ''
    if request.method == 'POST' and 'upload' in request.files:
        f = request.files.get('upload')
        fname, fext = os.path.splitext(f.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.config['CK_UPLOAD_PATH'],rnd_name)
        dirname = os.path.dirname(filepath)
        extension = f.filename.split('.')[1].lower()
        if extension not in ['jpg', 'gif', 'png', 'jpeg','svg']:
            return upload_fail(message='Images only. Filetype not allowed.')
        if not os.path.exists(dirname):
            try:    
                os.makedirs(dirname)
            except:
                error = "can't create directory."
        elif not os.access(dirname,os.W_OK):
            error = "can't write to directory."
        if not error: 
            if fext == ".gif" or fext == '.GIF':
                f.save(filepath)
                url = url_for('blog.uploaded_files', filename=rnd_name)
            else:     
                f.save(filepath)
                # compress the image
                img = Image.open(f)
                size = (700,700)
                img.thumbnail(size,Image.ANTIALIAS)
                img.save(filepath,quality=85,optimize=True)
                url = url_for('blog.uploaded_files', filename=rnd_name)
        return upload_success(url=url)# return upload_success call
        

# Flask-Ckeditor browse files on server
@blog_blueprint.route('/blog/files')
@login_required
@check_confirmed
@admin_required
def list_files():
    #Endpoint to list files on the server.
    files = []
    for filename in os.listdir(app.config['CK_UPLOAD_PATH']):
        path = os.path.join(app.config['CK_UPLOAD_PATH'], filename)
        if os.path.isfile(path):
            files.append({  "image"  :  "/files/" + filename  })
    return jsonify(files)