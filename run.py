#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys

from flask.ext.script import Manager, prompt, prompt_bool, prompt_pass
from flask.ext.sqlalchemy import get_debug_queries
from sqlalchemy.exc import DatabaseError

from esther import create_app, db, models
from esther.tests import run_tests
from esther.tests.angular.views import blueprint as angular_blueprint

app = create_app(['esther.settings.site'])
manager = Manager(app)

@manager.command
def server(toolbar=False, db_stats=False):
    app.debug = True
    app.register_blueprint(angular_blueprint, url_prefix='/tests/angular')

    if toolbar:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
        except ImportError:
            pass
        else:
            DebugToolbarExtension(app)

    if db_stats:
        @app.after_request
        def print_db_stats(response):
            queries = get_debug_queries()
            print u'↱ number of queries: {}'.format(len(queries))
            return response

    app.run()

@manager.shell
def make_shell_context():
    context = {
        'app': app,
        'db': db,
        'models': models
    }
    return context

@manager.command
def tests(label=None):
    kwargs = {}

    if label is not None:
        if not label.startswith('esther.tests'):
            label = 'esther.tests.{}'.format(label)
        kwargs['labels'] = [label]

    result = run_tests(**kwargs)

    if not result:
        sys.exit(1)

@manager.command
def database(action):
    if action == 'create':
        db.create_all()
    elif action == 'drop':
        db.drop_all()
    else:
        print(u'Invalid action: "{}"'.format(action))
        sys.exit(1)

@manager.command
def add_user():
    print(u'Set up a new user:')
    email = prompt('E-mail')
    short_name = prompt('Short name')
    full_name = prompt('Full name')
    password = prompt_pass('Password')
    is_admin = prompt_bool('Admin user')

    user = models.User(email=email, short_name=short_name, full_name=full_name,
                       password=password, is_admin=is_admin)

    db.session.add(user)

    try:
        db.session.commit()
    except DatabaseError as exc:
        print(u'Error creating user: \'{}\''.format(exc.message))
        sys.exit(1)

    print(u'User "{}" created.'.format(user.email))

if __name__ == '__main__':
    manager.run()
