import datetime

from flask import url_for, current_app
from flask.ext.login import UserMixin
import pytz
from sqlalchemy import types
from sqlalchemy.orm import subqueryload

from esther import db, bcrypt
from esther.decl_enum import DeclEnum
from esther.utils import slugify


def utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def obj_as_dict(obj, exclude=None):
    if exclude is None:
        exclude = []
    d = {}
    for column in obj.__table__.columns:
        if column.name not in exclude:
            d[column.name] = getattr(obj, column.name)
    return d


def prep_query_for_json(query):
    return [obj.as_dict() for obj in query]


class UTCDateTime(types.TypeDecorator):
    """ Adapted from: http://stackoverflow.com/a/2528453/171744. """
    impl = types.DateTime

    def __init__(self, timezone=True):
        super(UTCDateTime, self).__init__(timezone)

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(pytz.utc)
        return value

    def process_result_value(self, value, engine):
        if value is not None:
            if value.tzinfo is not None:
                return value.astimezone(pytz.utc)
            else:
                # For SQLite
                return value.replace(tzinfo=pytz.utc)
        return value


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    full_name = db.Column(db.String(128))
    short_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(128))
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, **columns):
        password = columns.pop('password', None)

        if password is not None:
            self.set_password(password)

        super(User, self).__init__(**columns)

    def __repr__(self):
        return u'<User "{}">'.format(self.email).encode('utf-8')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def is_active(self):
        return True if self.is_active_user is None else self.is_active_user


post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.UniqueConstraint('post_id', 'tag_id')
)


class PostStatus(DeclEnum):
    draft = 'draft', 'Draft'
    published = 'published', 'Published'
    retracted = 'retracted', 'Retracted'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    status = db.Column(PostStatus.db_type(), default=PostStatus.draft,
                       nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    body = db.Column(db.Text)
    pub_date = db.Column(UTCDateTime)
    created = db.Column(UTCDateTime, default=utc_now)
    modified = db.Column(UTCDateTime, default=utc_now, onupdate=utc_now)

    author = db.relation(User, backref=db.backref('posts', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts', lazy='dynamic'),
                           order_by=lambda: Tag.name)

    def __repr__(self):
        return u'<Post "{}">'.format(self.title).encode('utf-8')

    def publish(self, commit=True):
        self.status = PostStatus.published
        self.pub_date = utc_now()

        db.session.add(self)

        if commit:
            db.session.commit()

    @property
    def is_published(self):
        return self.status == PostStatus.published

    @property
    def url(self):
        if self.pub_date:
            return url_for('blog.view_post', year=self.pub_date.year,
                           month=self.pub_date.month, day=self.pub_date.day,
                           slug=self.slug)

    @property
    def continue_url(self):
        url = self.url
        if url:
            continue_frag = current_app.config['POST_CONTINUE_LINK_FRAGMENT']
            return u'{}#{}'.format(url, continue_frag)

    @property
    def preview(self):
        separator = current_app.config['POST_BODY_PREVIEW_SEPARATOR']
        parts = self.body.split(separator, 1)
        preview_part = parts[0].rstrip()

        if len(parts) == 2:
            return u'{}...'.format(preview_part)
        else:
            return preview_part

    @classmethod
    def get_published(cls, num=None):
        pub_date = Post.pub_date.desc()
        posts = cls.query.options(subqueryload(Post.tags)).filter_by(
            status=PostStatus.published).order_by(pub_date)
        return posts.limit(num) if num else posts

    @classmethod
    def get_recent(cls, page, num=None):
        if num is None:
            num = current_app.config['NUM_POSTS_PER_INDEX_PAGE']
        posts = cls.get_published()
        return posts.paginate(page, per_page=num)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name
        if not self.id and not self.slug:
            self.slug = slugify(unicode(name))

    def __repr__(self):
        return u'<Tag: "{}">'.format(self.name).encode('utf-8')

    @property
    def url(self):
        return url_for('blog.tag_posts', slug=self.slug)
