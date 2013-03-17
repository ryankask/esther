from urlparse import urljoin

from flask import Blueprint, current_app, url_for
from PyRSS2Gen import RSS2, RSSItem, Guid

from esther.models import Post

blueprint = Blueprint('feeds', __name__)

@blueprint.route('/blog')
def blog_posts():
    feed_config = current_app.config['FEEDS_CONFIG']['blog']
    base_url = url_for('general.index', _external=True)
    items = []
    posts = Post.get_published(num=10).all()

    for post in posts:
        post_url = urljoin(base_url, post.url)
        item = RSSItem(
            title=post.title,
            link=post_url,
            description=post.body.split('\r\n', 1)[0], # Add a real description?
            author='{} ({})'.format(post.author.email, post.author.full_name),
            categories=[tag.name for tag in post.tags],
            guid=Guid(post_url),
            pubDate=post.pub_date
        )
        items.append(item)

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
