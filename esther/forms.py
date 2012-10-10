from flask.ext.wtf import (Form, TextField, TextAreaField, Required, Length,
                           Email)

class ContactForm(Form):
    name = TextField(u'Name', [Required(), Length(min=2, max=128)])
    email = TextField(u'E-mail', [Required(), Email()])
    message = TextAreaField(u'Your message', [Required()])
