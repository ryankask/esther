from flask.ext.testing import TestCase

from esther import app


class EstherTestCase(TestCase):
    def create_app(self):
        app.config.from_object('esther.settings.test')
        return app
