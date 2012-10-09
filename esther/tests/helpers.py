from flask.ext.testing import TestCase

from esther import app, db


class EstherTestCase(TestCase):
    def create_app(self):
        app.config.from_object('esther.settings.test')
        return app


class EstherDBTestCase(EstherTestCase):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
