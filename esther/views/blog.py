from flask import Blueprint, request, flash, render_template, redirect, url_for
from flask.ext.login import login_required, current_user
import markdown
from sqlalchemy.sql import extract

from esther import db
from esther.forms import PostForm
from esther.models import PostStatus, Post, utc_now

blueprint = Blueprint('blog', __name__)

@blueprint.route('/posts')
@login_required
def view_posts():
    created = Post.created.desc()
    posts = Post.query.filter_by(author=current_user).order_by(created).all()
    return render_template('blog/post_list.html', posts=posts)

@blueprint.route('/posts/add', methods=('GET', 'POST'))
@login_required
def add_post():
    form = PostForm(request.form)

    if form.validate_on_submit():
        status = PostStatus.from_string(form.status.data)

        post = Post(author=current_user, title=form.title.data,
                    slug=form.slug.data, body=form.body.data,
                    status=status)

        if status == PostStatus.published:
            post.pub_date = utc_now()

        db.session.add(post)
        db.session.commit()

        message = u'Post "{0}" successfully added.'.format(form.title.data)
        flash(message, 'success')
        return redirect(url_for('.view_posts'))

    return render_template('blog/post_add.html', form=form)

@blueprint.route('/posts/<int:post_id>', methods=('GET', 'POST'))
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(request.form, obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.status = PostStatus.from_string(form.status.data)
        db.session.add(post)
        db.session.commit()

        message = u'Edited post "{0}".'.format(form.title.data)
        flash(message, 'success')
        return redirect(url_for('.view_posts'))

    return render_template('blog/post_edit.html', post=post, form=form)

@blueprint.route('/posts/<int:post_id>/preview', methods=('GET', 'POST'))
@login_required
def preview_post(post_id):
    post = Post.query.get_or_404(post_id)
    context = {
        'post': post,
        'post_body_html': markdown.markdown(post.body)
    }
    return render_template('blog/post_preview.html', **context)

### Public views

@blueprint.route('/<int:year>/<int(fixed_digits=2):month>/<int(fixed_digits=2):day>/<slug>')
def view_post(year, month, day, slug):
    post = Post.query.filter(
        (extract('year', Post.pub_date) == year) &
        (extract('month', Post.pub_date) == month) &
        (extract('day', Post.pub_date) == day) &
        (Post.status == PostStatus.published) &
        (Post.slug == slug)).first_or_404()

    context = {
        'post': post,
        'post_body_html': markdown.markdown(post.body)
    }
    return render_template('blog/post_view.html', **context)
