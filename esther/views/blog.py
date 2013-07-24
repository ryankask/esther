from urlparse import urljoin

from flask import (Blueprint, request, flash, render_template, redirect,
                   url_for, abort, current_app)
from flask.ext.login import login_required, current_user
from PyRSS2Gen import RSS2, RSSItem, Guid
from sqlalchemy import and_, extract
from sqlalchemy.orm import subqueryload

from esther import db
from esther.forms import PostForm
from esther.models import PostStatus, Post, utc_now, Tag

blueprint = Blueprint('blog', __name__)


@blueprint.route('/posts', defaults={'page': 1})
@blueprint.route('/posts/page/<int:page>')
@login_required
def view_posts(page):
    created = Post.created.desc()
    posts = Post.query.options(subqueryload(Post.tags)).filter_by(
        author=current_user).order_by(created)
    per_page = current_app.config['NUM_POSTS_PER_LIST_PAGE']
    paginated_posts = posts.paginate(page, per_page)
    return render_template('blog/post_list.html', posts=paginated_posts)


@blueprint.route('/posts/add', methods=('GET', 'POST'))
@login_required
def add_post():
    form = PostForm(request.form)

    if form.validate_on_submit():
        status = PostStatus.from_string(form.status.data)

        post = Post(author=current_user, title=form.title.data,
                    slug=form.slug.data, body=form.body.data,
                    status=status, tags=form.tags.data)

        if status == PostStatus.published:
            post.pub_date = utc_now()

        db.session.add(post)
        db.session.commit()

        message = u'Post "{}" successfully added.'.format(form.title.data)
        flash(message, 'success')
        return redirect(url_for('.view_posts'))

    return render_template('blog/post_add.html', form=form)


@blueprint.route('/posts/<int:post_id>', methods=('GET', 'POST'))
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(author=current_user, id=post_id).first_or_404()
    form = PostForm(request.form, obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)

        if (post.pub_date is None and post.status == PostStatus.published):
            post.pub_date = utc_now()

        db.session.commit()
        message = u'Edited post "{}".'.format(form.title.data)
        flash(message, 'success')
        return redirect(url_for('.view_posts'))

    return render_template('blog/post_edit.html', post=post, form=form)


@blueprint.route('/posts/<int:post_id>/preview', methods=('GET', 'POST'))
@login_required
def preview_post(post_id):
    post = Post.query.filter_by(author=current_user, id=post_id).first_or_404()
    return render_template('blog/post_preview.html', post=post)


### Public views


@blueprint.route('/<int:year>/<int(fixed_digits=2):month>/<int(fixed_digits=2):day>/<slug>')
def view_post(year, month, day, slug):
    post = Post.query.filter(
        (extract('year', Post.pub_date) == year) &
        (extract('month', Post.pub_date) == month) &
        (extract('day', Post.pub_date) == day) &
        (Post.status == PostStatus.published) &
        (Post.slug == slug)).first_or_404()
    return render_template('blog/post_view.html', post=post)


@blueprint.route('/<int:year>')
@blueprint.route('/<int:year>/<int(fixed_digits=2):month>')
@blueprint.route('/<int:year>/<int(fixed_digits=2):month>/<int(fixed_digits=2):day>')
def post_archive(year, month=None, day=None):
    filters = [Post.status == PostStatus.published,
               extract('year', Post.pub_date) == year]

    if month:
        filters.append(extract('month', Post.pub_date) == month)
    if day:
        filters.append(extract('day', Post.pub_date) == day)

    posts = Post.query.filter(and_(*filters)).order_by(Post.pub_date).all()

    if not posts:
        abort(404)

    return render_template('blog/post_archive.html', posts=posts, year=year,
                           month=month, day=day)


@blueprint.route('/tags', defaults={'page': 1})
@blueprint.route('/tags/page/<int:page>')
def tag_list(page):
    has_published_post = Tag.posts.any(Post.status == PostStatus.published)
    tags = Tag.query.order_by(Tag.name).filter(has_published_post)
    per_page = current_app.config['NUM_TAGS_PER_LIST_PAGE']
    paginated_tags = tags.paginate(page, per_page)
    return render_template('blog/tag_list.html', tags=paginated_tags)


@blueprint.route('/tags/<slug>', defaults={'page': 1})
@blueprint.route('/tags/<slug>/page/<int:page>')
def tag_posts(slug, page):
    has_published_post = Tag.posts.any(Post.status == PostStatus.published)
    tag = Tag.query.filter(has_published_post, Tag.slug == slug).first_or_404()
    posts = Post.query.filter(Post.status == PostStatus.published,
                              Post.tags.any(Tag.id == tag.id))
    per_page = current_app.config['NUM_POSTS_PER_TAG_PAGE']
    paginated_posts = posts.paginate(page, per_page)
    return render_template('blog/tag_posts.html', tag=tag,
                           posts=paginated_posts)


### Feeds


@blueprint.route('/posts/feed')
def posts_feed():
    base_url = url_for('general.index', _external=True)
    items = []
    posts = Post.get_published(num=10).all()

    for post in posts:
        post_url = urljoin(base_url, post.url)

        # TODO: Add a real description
        item = RSSItem(
            title=post.title,
            link=post_url,
            description=post.body.split('\r\n', 1)[0],
            author='{} ({})'.format(post.author.email, post.author.full_name),
            categories=[tag.name for tag in post.tags],
            guid=Guid(post_url),
            pubDate=post.pub_date
        )
        items.append(item)

    feed_config = current_app.config['BLOG_POSTS_FEED']
    rss2_feed = RSS2(
        title=feed_config['title'],
        link=base_url,
        description=feed_config['description'],
        language='en-us',
        webMaster=feed_config['webmaster'],
        lastBuildDate=posts[0].pub_date if posts else None,
        ttl=1440,
        items=items
    )
    return current_app.response_class(rss2_feed.to_xml(encoding='utf-8'),
                                      mimetype='application/rss+xml')
