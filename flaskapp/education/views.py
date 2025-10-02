"""
Contains view functions and routes for posts "education" section .
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from flaskapp.education.forms import CreatePostForm
from flaskapp.extensions import db, roles_required
from flaskapp.models.blog_post import BlogPost
from flaskapp.models.user import User

bp = Blueprint('education', __name__, template_folder='templates')


@bp.route('/posts/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_posts():
    post_form = CreatePostForm()

    if post_form.validate_on_submit():
        post_id = request.form.get('id')
        post = BlogPost.query.get_by_id(post_id)

        if post:
            if 'edit' in request.form:
                post.title = request.form.get('title')
                post.content = request.form.get('content')
                db.session.commit()
            elif 'delete' in request.form:
                db.session.delete(post)
                db.session.commit()
    else:
        print(post_form.errors)

    return redirect(url_for('education.view_all_posts'))


@login_required
@bp.route("/posts/<id>", methods=["GET", "POST"])
def view_post(id):
    post_form = CreatePostForm()
    all_posts = BlogPost.query.all()
    if current_user.is_authenticated:
        my_posts = BlogPost.query.filter_by(author_id=current_user.id).all()
    else:
        my_posts = []
    digests = BlogPost.query.filter(BlogPost.title.ilike('%Highlights%')).all()
    post = BlogPost.query.get_by_id(id)
    author = User.query.filter_by(id=post.author_id).first()
    author_name = author.username
    return render_template("education/education_main.html", author_name=author_name, post=post, all_posts=all_posts, my_posts=my_posts, digests=digests, postForm=post_form)


@login_required
@bp.route("/posts", methods=['GET', 'POST'])
def view_all_posts():
    post_form = CreatePostForm()
    all_posts = BlogPost.query.all()
    post = BlogPost.query.first()
    author = User.query.filter_by(id=post.author_id).first()
    author_name = author.username
    if current_user.is_authenticated:
        my_posts = BlogPost.query.filter_by(author_id=current_user.id).all()
    else:
        my_posts = []
    digests = BlogPost.query.filter(BlogPost.title.ilike('%Highlights%')).all()

    return render_template("education/education_main.html", author_name=author_name, all_posts=all_posts, my_posts=my_posts, digests=digests, postForm=post_form, post=post)


@login_required
@roles_required('admin')
@bp.route("/posts/new_post", methods=["POST"])
def new_post():
    new_post_form = CreatePostForm()
    if new_post_form.validate_on_submit():
        new_post = BlogPost(
            author_id=current_user.id,
            title=new_post_form.title.data,
            content=new_post_form.content.data
        )
        db.session.add(new_post)
        db.session.commit()
    return redirect(url_for('education.view_all_posts'))
