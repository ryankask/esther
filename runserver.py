#!/usr/bin/env python
from esther import app

app.debug = True

try:
    from flask_debugtoolbar import DebugToolbarExtension
except ImportError:
    pass
else:
    DebugToolbarExtension(app)

app.run()
