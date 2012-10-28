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


class PageMixin(object):
    def assert_page(self, url, template):
        response = self.client.get(url)
        self.assert_200(response)
        self.assert_template_used(template)
