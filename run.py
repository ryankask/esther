#!/usr/bin/env python
import sys

from flask.ext.script import Manager

from esther import app

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

if __name__ == '__main__':
    manager.run()
