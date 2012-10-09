from flask.ext.testing import TestCase

from esther import create_app, db


class EstherTestCase(TestCase):
    def create_app(self):
        return create_app(['esther.settings.site', 'esther.settings.test'])


class EstherDBTestCase(EstherTestCase):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
