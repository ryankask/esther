import sys

from flask.json import dump
from sqlalchemy.orm import joinedload, subqueryload

from esther.models import obj_as_dict, Post, PostStatus


def export_posts():
    data = []
    opts = (joinedload(Post.author), subqueryload(Post.tags))
    posts = Post.query.options(*opts).filter(
        Post.status == PostStatus.published).order_by(Post.created)

    for post in posts:
        post_data = obj_as_dict(post)
        post_data['status'] = post_data['status'].value
        post_data['author'] = obj_as_dict(post.author)
        del post_data['author']['password']
        post_data['tags'] = [obj_as_dict(tag) for tag in post.tags]
        data.append(post_data)

    dump(data, sys.stdout)
