from flask.ext.wtf import (Form, TextField, TextAreaField, PasswordField,
                           Required, Length, Email)

from esther import bcrypt
from esther.models import User


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
