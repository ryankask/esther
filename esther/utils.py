from esther import db
from esther.models import User, get_columns

def add_user(email, short_name, commit=True, **other_fields):
    user = User(email=email, short_name=short_name)

    columns = get_columns(User)
    for field, value in other_fields.items():
        if field in columns:
            setattr(user, field, value)

    db.session.add(user)

    if commit:
        db.session.commit()

    return user
