#!/usr/bin/env python
import sys

from flask.ext.script import Manager, prompt, prompt_bool, prompt_pass
from sqlalchemy.exc import DatabaseError

from esther import create_app, db
from esther.models import User

app = create_app(['esther.settings.site'])
manager = Manager(app)

@manager.command
def server():
    app.debug = True

    try:
        from flask_debugtoolbar import DebugToolbarExtension
    except ImportError:
        pass
    else:
        DebugToolbarExtension(app)

    app.run()

@manager.command
def tests():
    from esther.tests import run_tests
    result = run_tests()

    if not result:
        sys.exit(1)

@manager.command
def database(action):
    if action == 'create':
        db.create_all()
    elif action == 'drop':
        db.drop_all()
    else:
        print(u'Invalid action: "{0}"'.format(action))
        sys.exit(1)

@manager.command
def add_user():
    print(u'Set up a new user:')
    email = prompt('E-mail')
    short_name = prompt('Short name')
    full_name = prompt('Full name')
    password = prompt_pass('Password')
    is_admin = prompt_bool('Admin user')

    user = User(email=email, short_name=short_name, full_name=full_name,
                password=password, is_admin=is_admin)

    db.session.add(user)

    try:
        db.session.commit()
    except DatabaseError as exc:
        print(u'Error creating user: \'{0}\''.format(exc.message))
        sys.exit(1)

    print(u'User "{0}" created.'.format(user.email))

if __name__ == '__main__':
    manager.run()
