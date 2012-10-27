from sqlalchemy.sql import exists
from flask.ext.wtf import (Form, TextField, TextAreaField, PasswordField,
                           SelectField, ValidationError, Required, Length, Email)

from esther import bcrypt, db
from esther.models import User, PostStatus, Post


class ContactForm(Form):
    name = TextField(u'Name', [Required(), Length(min=2, max=128)])
    email = TextField(u'E-mail', [Required(), Email()])
    message = TextAreaField(u'Your message', [Required()])


class LoginForm(Form):
    email = TextField(u'E-mail', [Required(), Email()])
    password = PasswordField(u'Password', [Required()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None
        self.auth_failed = False

    def validate(self, *args, **kwargs):
        success = super(LoginForm, self).validate(*args, **kwargs)
        if not success:
            return success

        user = User.query.filter_by(email=self.email.data,
                                    is_active_user=True).first()

        if (user is not None and
            bcrypt.check_password_hash(user.password, self.password.data)):
            self.user = user
            return True

        self.auth_failed = True
        return False


class StatusField(SelectField):
    def populate_obj(self, obj, name):
        setattr(obj, name, PostStatus.from_string(self.data))


class PostForm(Form):
    title = TextField(u'Title', [Required(), Length(max=255)])
    slug = TextField(u'Slug', [Required(), Length(max=80)])
    status = StatusField(u'Status', choices=[(v, h) for v, h in PostStatus])
    body = TextAreaField(u'Post body', [Required()])

    def validate_slug(form, field):
        # Only validate the slug if there is no object data for the field
        # (a Post is being added) or an edited post's slug is being changed.
        # Then do a really clunky EXISTS.
        if (field.object_data != field.data and
            db.session.query(exists().where(Post.slug == field.data)).scalar()):
            raise ValidationError(u'Slug already used by another post.')
