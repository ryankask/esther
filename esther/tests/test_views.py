from esther.tests.helpers import EstherTestCase


class GeneralTests(EstherTestCase):
    def test_home(self):
        response = self.client.get('/')
        self.assert_200(response)
        self.assert_template_used('general/index.html')

    def test_404(self):
        response = self.client.get('/_404')
        self.assert_404(response)
        self.assert_template_used('errors/404.html')
