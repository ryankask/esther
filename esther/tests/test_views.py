from flask.ext.login import login_required
from werkzeug.urls import url_quote_plus

from esther import db, mail
from esther.models import User
from esther.tests.helpers import EstherTestCase, EstherDBTestCase


class PageMixin(object):
    def assert_page(self, url, template):
        response = self.client.get(url)
        self.assert_200(response)
        self.assert_template_used(template)


class GeneralTests(EstherTestCase, PageMixin):
    def test_home(self):
        self.assert_page('/', 'general/index.html')

    def test_about(self):
        self.assert_page('/about', 'general/about.html')

    def test_contact(self):
        self.assert_page('/contact', 'general/contact.html')

    def test_contact_form_submission(self):
        form_data = {
            'name': 'John Smith',
            'email': 'john@example.com',
            'message': 'Thanks for getting in touch with me...'
        }

        with mail.record_messages() as outbox:
            response = self.client.post('/contact', data=form_data,
                                        follow_redirects=True)

            # Check that the e-mail was sent
            self.assertEqual(len(outbox), 1)

            for value in form_data.values():
                self.assertTrue(value in outbox[0].body)

        # Test that the user is redirected home and shown a success message
        self.assert_template_used('general/index.html')
        self.assertTrue('id="messages"' in response.data)


class AuthTests(EstherDBTestCase, PageMixin):
    def add_protected_view(self):
        url = '/_protected'
        quoted_url = url_quote_plus('/_protected')
        self.redirect_url = '/login?next={0}'.format(quoted_url)

        @self.app.route(url)
        @login_required
        def protected():
            return 'success'

    def create_user(self):
        user = User(email='ryan@example.com', short_name='Ryan',
                    password='password')
        db.session.add(user)
        db.session.commit()

        self.login_data = {
            'email': user.email,
            'password': 'password'
        }

        return user

    def test_login_page(self):
        self.assert_page('/login', 'auth/login.html')

    def test_login_required_redirects_to_login_page(self):
        self.add_protected_view()
        self.assert_redirects(self.client.get('/_protected'), self.redirect_url)

    def test_login_success(self):
        self.create_user()
        self.client.post('/login', data=self.login_data)

        self.add_protected_view()
        response = self.client.get('/_protected')
        self.assertEqual(response.data, 'success')

    def test_login_with_next_param(self):
        self.create_user()
        response = self.client.post('/login?next=/about', data=self.login_data)
        self.assert_redirects(response, '/about')

    def assert_login_failure(self, email, password):
        self.create_user()
        response = self.client.post('/login', data={
            'email': email,
            'password': password
        })

        self.assert_template_used('auth/login.html')
        self.assertTrue('Incorrect e-mail and/or password' in response.data)

        form = self.get_context_variable('form')
        self.assertEqual(form.user, None)
        self.assertEqual(form.auth_failed, True)

    def test_login_failed_bad_email(self):
        self.assert_login_failure('bryan@example.com', 'password')

    def test_login_failed_bad_password(self):
        self.assert_login_failure('ryan@example.com', 'wrong_password')

    def test_logout_success(self):
        self.create_user()
        self.client.post('/login', data=self.login_data)

        self.add_protected_view()
        response = self.client.get('/_protected')
        self.assertEqual(response.data, 'success')

        self.assertRedirects(self.client.get('/logout'), '/')
        self.assert_redirects(self.client.get('/_protected'), self.redirect_url)

    def test_logout_with_next_param(self):
        self.assertRedirects(self.client.get('/logout?next=/about'), '/about')


class ErrorTests(EstherTestCase):
    def test_404(self):
        response = self.client.get('/_404')
        self.assert_404(response)
        self.assert_template_used('errors/404.html')
