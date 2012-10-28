from flask import url_for
from werkzeug.datastructures import MultiDict

from esther import db
from esther.forms import PostForm
from esther.models import PostStatus, Post, utc_now
from esther.tests.helpers import EstherDBTestCase, PageMixin
from esther.tests.views.test_auth import AuthMixin


class BlogMixin(AuthMixin):
    def create_post(self, user, **kwargs):
        post = Post(author=user, title=u'My First Post', slug=u'my-first-post',
                    body='Post body', **kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    def create_post_and_login(self, post_data=None):
        post_data = post_data or {}
        user = self.create_user(commit=False)
        post = self.create_post(user, **post_data)
        self.login(create_user=False)
        return post


class AdminTests(EstherDBTestCase, BlogMixin, PageMixin):
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
        self.assertEqual(form.errors['slug'], [u'Slug is not unique.'])

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
        self.assert_redirects(response, url_for('blog.view_posts'))

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

    def assert_author_only(self, view):
        john = self.create_user(email='john@example.com')
        post = self.create_post(john)
        # Login as a different user and try to edit John's post
        self.login()
        response = self.client.get(url_for(view, post_id=post.id))
        self.assert_404(response)

    def test_edit_as_non_author_aborts(self):
        self.assert_author_only('blog.edit_post')

    def test_preview_post(self):
        post = self.create_post_and_login()
        self.assert_page(u'/blog/posts/{0}/preview'.format(post.id),
                         'blog/post_preview.html')

    def test_preview_non_author_aborts(self):
        self.assert_author_only('blog.preview_post')


class PublicTests(EstherDBTestCase, BlogMixin, PageMixin):
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
