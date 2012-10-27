from flask import url_for
from flask.ext.login import login_required
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_quote_plus

from esther import db, mail
from esther.forms import PostForm
from esther.models import User, PostStatus, Post, utc_now
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
        self.assertTrue('class="alert-box success"' in response.data)


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


class BlogTests(EstherDBTestCase, PageMixin):
    def create_user(self, commit=True):
        user = User(email='ryan@example.com', short_name='Ryan',
                    password='password')
        db.session.add(user)

        if commit:
            db.session.commit()

        return user

    def create_post(self, user, **kwargs):
        post = Post(author=user, title=u'My First Post', slug=u'my-first-post',
                    body='Post body', **kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    def login(self, create_user=True):
        if create_user:
            self.create_user()

        self.client.post('/login', data={'email': 'ryan@example.com',
                                         'password': 'password'})

    def create_post_and_login(self, post_data=None):
        post_data = post_data or {}
        user = self.create_user(commit=False)
        post = self.create_post(user, **post_data)
        self.login(create_user=False)
        return post

    ### Admin view tests

    def test_post_list(self):
        post = self.create_post_and_login()
        self.client.get('/blog/posts')
        self.assert_template_used('blog/post_list.html')

        posts = self.get_context_variable('posts')
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], post)

    def test_add_post_page(self):
        self.login()
        self.assert_page('/blog/posts/add', 'blog/post_add.html')

    def test_used_slug_raises_validation_error(self):
        post = self.create_post(self.create_user(commit=False))
        form_data = MultiDict({'title': 'My Second Post', 'slug': post.slug,
                               'status': PostStatus.draft, 'body': 'Welcome'})
        form = PostForm(form_data)
        self.assertFalse(form.validate())
        self.assertEqual(form.errors['slug'],
                         [u'Slug already used by another post.'])

    def test_add_post_success(self):
        user = self.create_user()
        self.login(create_user=False)

        post_data = {
            'title': 'New Railroad Opens',
            'slug': 'new-railroad-opens',
            'status': PostStatus.published.value,
            'body': 'A new railroad is opening tomorrow.'
        }

        response = self.client.post(url_for('blog.add_post'), data=post_data)
        self.assertRedirects(response, url_for('blog.view_posts'))

        post = Post.query.filter_by(slug=post_data['slug']).first()
        self.assertEqual(post.author, user)
        self.assertEqual(post.title, post_data['title'])
        self.assertEqual(post.body, post_data['body'])
        self.assertEqual(post.status, PostStatus.published)

        # Make sure ``pub_date`` is set if the post is being published
        # immediatley
        self.assertNotEqual(post.pub_date, None)

    def test_edit_post_page(self):
        post = self.create_post_and_login({
            'status': PostStatus.published,
            'pub_date': utc_now()
        })
        self.client.get(url_for('blog.edit_post', post_id=post.id))
        self.assert_template_used('blog/post_edit.html')

        form = self.get_context_variable('form')
        self.assertEqual(form.title.data, post.title)
        self.assertEqual(form.status.data, 'published')
        self.assertEqual(form.body.data, u'Post body')

    def test_edit_post_success(self):
        post = self.create_post_and_login()
        edit_data = {
            'title': 'My first edited post',
            'slug': post.slug,
            'status': PostStatus.published.value,
            'body': 'Some different text',
        }

        response = self.client.post(url_for('blog.edit_post', post_id=post.id),
                                    data=edit_data)
        self.assert_redirects(response, url_for('blog.view_posts'))

        edited_post = Post.query.get(post.id)
        self.assertEqual(edited_post.title, 'My first edited post')
        self.assertEqual(edited_post.slug, post.slug)
        self.assertEqual(edited_post.status, PostStatus.published)
        self.assertEqual(edited_post.body, 'Some different text')

    def test_preview_post(self):
        post = self.create_post_and_login()
        self.assert_page(u'/blog/posts/{0}/preview'.format(post.id),
                         'blog/post_preview.html')

    ### Public view tests

    def test_view_post(self):
        post = self.create_post(self.create_user())
        now = utc_now()
        url = url_for('blog.view_post', year=now.year, month=now.month,
                      day=now.day, slug=post.slug)
        self.assert_404(self.client.get(url))
        post.publish()
        self.assert_page(url, 'blog/post_view.html')

    def assert_archive(self, posts, **date_components):
        url = url_for('blog.post_archive', **date_components)
        self.assert_page(url, 'blog/post_archive.html')
        self.assertEqual(set(self.get_context_variable('posts')), set(posts))

    def test_post_archive(self):
        now = utc_now()
        posts = [
            self.create_post(self.create_user(), status=PostStatus.published,
                             pub_date=now)
        ]

        self.assert_archive(posts, year=now.year)
        self.assert_archive(posts, year=now.year, month=now.month)
        self.assert_archive(posts, year=now.year, month=now.month, day=now.day)


class ErrorTests(EstherTestCase):
    def test_404(self):
        response = self.client.get('/_404')
        self.assert_404(response)
        self.assert_template_used('errors/404.html')
