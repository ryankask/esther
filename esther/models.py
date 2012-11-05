import datetime

from flask import url_for, current_app
from flask.ext.login import UserMixin
import pytz
from sqlalchemy import types

from esther import db, bcrypt
from esther.decl_enum import DeclEnum

def utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class UTCDateTime(types.TypeDecorator):
    """ Adapted from: http://stackoverflow.com/a/2528453/171744. """
    impl = types.DateTime

    def __init__(self, timezone=True):
        super(UTCDateTime, self).__init__(timezone)

    def process_bind_param(self, value, enging):
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
        return u'<User "{0}">'.format(self.email)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def is_active(self):
        return True if self.is_active_user is None else self.is_active_user


class PostStatus(DeclEnum):
    draft = 'draft', 'Draft'
    published = 'published', 'Published'
    retracted = 'retracted', 'Retracted'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(PostStatus.db_type(), default=PostStatus.draft,
                       nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    body = db.Column(db.Text)
    pub_date = db.Column(UTCDateTime)
    created = db.Column(UTCDateTime, default=utc_now)
    modified = db.Column(UTCDateTime, default=utc_now, onupdate=utc_now)

    author = db.relation(User, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return u'<Post "{0}">'.format(self.title)

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
    def preview(self):
        separator = current_app.config['POST_BODY_PREVIEW_SEPARATOR']
        return self.body.split(separator, 1)[0].rstrip()
