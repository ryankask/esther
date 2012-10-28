from flask import url_for
from flask.ext.login import login_required
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_quote_plus

from esther import db
from esther.forms import UserForm
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


class UserManagementTests(EstherDBTestCase, AuthMixin, PageMixin):
    def create_admin(self, **kwargs):
        kwargs['is_admin'] = True
        return self.create_user(**kwargs)

    def create_admin_and_login(self):
        admin = self.create_admin()
        response = self.login(create_user=False)
        return admin, response

    def test_list_users_as_non_admin_forbidden(self):
        self.login()
        self.assert_403(self.client.get(url_for('auth.list_users')))

    def test_list_users(self):
        admin = self.create_admin_and_login()[0]
        self.assert_page(url_for('auth.list_users'), 'auth/user_list.html')
        users = self.get_context_variable('users')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], admin)

    def test_add_user(self):
        self.create_admin_and_login()
        new_user_data = {
            'email': 'john@example.com',
            'full_name': 'John Smith',
            'short_name': 'John',
            'password': 'password',
            'is_admin': False
        }
        response = self.client.post(url_for('auth.add_user'), data=new_user_data)
        self.assert_redirects(response, url_for('auth.list_users'))
        user = User.query.filter_by(email='john@example.com').first()
        # Just check that the e-mail and full name are set; wtforms is doing
        # its job
        self.assertEqual(user.full_name, 'John Smith')

    def test_email_validation(self):
        user = self.create_user()
        form_data = MultiDict({'email': user.email, 'short_name': 'John'})
        form = UserForm(form_data)
        self.assertFalse(form.validate())
        self.assertEqual(form.errors['email'], [u'E-mail is not unique.'])
