#!/usr/bin/env python
import sys

from flask.ext.script import Manager

from esther import create_app, db

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

if __name__ == '__main__':
    manager.run()
