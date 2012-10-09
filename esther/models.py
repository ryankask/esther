import sqlalchemy

from esther import db, bcrypt

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

    def __init__(self, email, short_name, password=None):
        self.email = email
        self.short_name = short_name

        if password is not None:
            self.set_password(password)

    def __unicode__(self):
        return u'<User {0}>'.format(self.email)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
