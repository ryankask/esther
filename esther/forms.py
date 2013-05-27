import re

from flask import current_app
from flask.ext.wtf import (Form, Field, TextField, TextAreaField, PasswordField,
                           BooleanField, SelectField, DateTimeField,
                           ValidationError, Required, Length, Email,
                           HiddenInput, TextInput)
from sqlalchemy.sql import exists
from wtforms.ext.dateutil.fields import DateTimeField as ExtDateTimeField


from esther import bcrypt, db
from esther.models import User, PostStatus, Post, Tag, List

### Validators

def unique(column, message=None):
    if message is None:
        message = u'{} is not unique.'

    def validator(form, field):
        if (field.object_data != field.data and
            db.session.query(exists().where(column == field.data)).scalar()):
            label_text = re.sub(r'\([^)]*\)', '', field.label.text).strip()
            raise ValidationError(message.format(label_text))

    return validator


### General


class ContactForm(Form):
    name = TextField(u'Name', [Required(), Length(min=2, max=128)])
    email = TextField(u'E-mail', [Required(), Email()])
    message = TextAreaField(u'Your message', [Required()])


### Auth


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


class ChangePasswordField(PasswordField):
    def populate_obj(self, obj, name):
        if obj and self.data:
            obj.set_password(self.data)


class UserForm(Form):
    email = TextField(u'E-mail', [Required(), Email(), unique(User.email)])
    full_name = TextField(u'Full name')
    short_name = TextField(u'Short name', [Required()])
    password = ChangePasswordField(u'Password')
    is_admin = BooleanField(u'Is admin?')


class AddUserForm(UserForm):
    password = PasswordField(u'Password', [Required()])


### Blog


class StatusField(SelectField):
    def populate_obj(self, obj, name):
        setattr(obj, name, PostStatus.from_string(self.data))

    def process_data(self, value):
        """ If the field is being populated by a ``Post`` object, set its
        value to the field's string representation. """
        try:
            self.data = value.value
        except AttributeError:
            self.data = value


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join([tag.name for tag in self.data])
        return u''

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            # Order is preserved here but ``Post.tags`` orders by tag name
            seen = set()
            tag_names = []
            for value in valuelist[0].split(','):
                stripped_value = value.strip()
                if stripped_value and stripped_value not in seen:
                    tag_names.append(stripped_value)
                    seen.add(stripped_value)

            existing_tags = Tag.query.filter(Tag.name.in_(tag_names))
            existing_tag_names = {t.name: t for t in existing_tags}

            tags = []
            for tag_name in tag_names:
                try:
                    tags.append(existing_tag_names[tag_name])
                except KeyError:
                    tags.append(Tag(tag_name))

            self.data = tags
        else:
            self.data = []


class UTCDateTimeField(DateTimeField):
    def populate_obj(self, obj, name):
        if self.data:
            dt = self.data
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                timezone = current_app.config['TIME_ZONE']
                dt = timezone.localize(self.data, is_dst=None)
            setattr(obj, name, dt)


class PostForm(Form):
    title = TextField(u'Title', [Required(), Length(max=255)])
    slug = TextField(u'Slug (press s to generate from title)',
                     [Required(), Length(max=80), unique(Post.slug)])
    status = StatusField(u'Status', choices=[(v, h) for v, h in PostStatus])
    pub_date = UTCDateTimeField(u'Date Published')
    body = TextAreaField(u'Post body', [Required()], widget=HiddenInput())
    tags = TagListField(u'Tags')


### Todo


class ListForm(Form):
    title = TextField(u'Title', [Required(), Length(max=128)])
    description = TextAreaField(u'Description', [Required()])
    is_public = BooleanField(u'Is public?')

    def validate_title(form, field):
        title_cond = List.slug == List.slugify(field.data)
        if (field.object_data != field.data and
            db.session.query(exists().where(title_cond)).scalar()):
            raise ValidationError('Invalid title. Please choose another.')

    def populate_obj(self, obj):
        super(ListForm, self).populate_obj(obj)
        obj.generate_slug()


class ItemForm(Form):
    content = TextField(u'Content', [Required(), Length(max=255)])
    details = TextAreaField(u'Details', [Length(max=2048)])
    is_done = BooleanField(u'Is done?')
    due = ExtDateTimeField(u'Due')
