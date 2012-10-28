from flask.ext.login import login_required
from werkzeug.urls import url_quote_plus

from esther import db
from esther.models import User
from esther.tests.helpers import EstherDBTestCase, PageMixin


class AuthMixin(object):
    def create_user(self, commit=True, **kwargs):
        user_data = {
            'email': 'ryan@example.com',
            'short_name': 'Ryan',
            'password': 'password'
        }
        user_data.update(kwargs)
        user = User(**user_data)
        db.session.add(user)

        if commit:
            db.session.commit()

        return user

    def login(self, create_user=True, url=None):
        if create_user:
            self.create_user()

        if url is None:
            url = '/login'

        return self.client.post(url, data={'email': 'ryan@example.com',
                                           'password': 'password'})


class AuthTests(EstherDBTestCase, AuthMixin, PageMixin):
    def add_protected_view(self):
        url = '/_protected'
        quoted_url = url_quote_plus('/_protected')
        self.redirect_url = '/login?next={0}'.format(quoted_url)

        @self.app.route(url)
        @login_required
        def protected():
            return 'success'

    def test_login_page(self):
        self.assert_page('/login', 'auth/login.html')

    def test_login_required_redirects_to_login_page(self):
        self.add_protected_view()
        self.assert_redirects(self.client.get('/_protected'), self.redirect_url)

    def test_login_success(self):
        self.login()
        self.add_protected_view()
        response = self.client.get('/_protected')
        self.assertEqual(response.data, 'success')

    def test_login_with_next_param(self):
        response = self.login(url='/login?next=/about')
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
        self.login()
        self.add_protected_view()
        response = self.client.get('/_protected')
        self.assertEqual(response.data, 'success')

        self.assert_redirects(self.client.get('/logout'), '/')
        self.assert_redirects(self.client.get('/_protected'), self.redirect_url)

    def test_logout_with_next_param(self):
        self.assert_redirects(self.client.get('/logout?next=/about'), '/about')
