import sqlalchemy

from esther import db

def get_columns(model):
    return [prop.key for prop in model.__mapper__.iterate_properties
            if isinstance(prop, sqlalchemy.orm.ColumnProperty)]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    full_name = db.Column(db.String(255))
    short_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email, short_name):
        self.email = email
        self.short_name = short_name

    def __unicode__(self):
        return u'<User {0}>'.format(self.email)
