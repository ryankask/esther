from esther.tests.helpers import EstherTestCase


class GeneralTests(EstherTestCase):
    def test_home(self):
        response = self.client.get('/')
        self.assert_200(response)
        self.assert_template_used('general/index.html')

    def test_about(self):
        response = self.client.get('/about')
        self.assert_200(response)
        self.assert_template_used('general/about.html')

    def test_contact(self):
        response = self.client.get('/contact')
        self.assert_200(response)
        self.assert_template_used('general/contact.html')

    def test_contact_form_submission(self):
        form_data = {
            'name': 'John Smith',
            'email': 'john@example.com',
            'message': 'Thanks for getting in touch with me...'
        }
        response = self.client.post('/contact', data=form_data,
                                    follow_redirects=True)

        # Check that the page redirected and that the flash message
        # is displayed.
        self.assert_template_used('general/index.html')
        self.assertTrue('id="messages"' in response.data)


class ErrorTests(EstherTestCase):
    def test_404(self):
        response = self.client.get('/_404')
        self.assert_404(response)
        self.assert_template_used('errors/404.html')
