from flask import Blueprint, request, flash, render_template, redirect, url_for
from flask.ext.login import login_required, current_user

from esther import db
from esther.forms import PostForm
from esther.models import PostStatus, Post, utc_now

blueprint = Blueprint('blog', __name__)

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

        flash(u'Post "{0}" successfully added'.format(form.title.data))
        return redirect(url_for('general.index'))

    return render_template('blog/post_add.html', form=form)
