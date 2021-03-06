import datetime

from esther import db
from esther.models import User, Post, PostStatus, Tag
from esther.tests.helpers import EstherTestCase, EstherDBTestCase


class UserTests(EstherTestCase):
    def init_user(self, **kwargs):
        return User(email='ryan@example.com', short_name='Ryan', **kwargs)

    def test_set_password(self):
        user = self.init_user()
        user.set_password('password')
        self.assertNotEqual(user.password, 'password')

    def test_is_active(self):
        user = self.init_user()
        self.assertTrue(user.is_active())

        user.is_active_user = False
        self.assertFalse(user.is_active())


class PostTests(EstherDBTestCase):
    def create_post(self, create_user=True, **kwargs):
        post_data = {
            'title': 'First Tiger on the Moon',
            'slug': 'first-tiger-moon',
            'body': 'The contents.'
        }

        if 'author' not in kwargs:
            user = User(email='ryan@example.com', short_name='Ryan')
            db.session.add(user)
            post_data['author'] = user

        post_data.update(kwargs)
        post = Post(**post_data)

        db.session.add(post)
        db.session.commit()

        return post

    def test_publish(self):
        post = self.create_post()
        self.assertEqual(post.status, PostStatus.draft)
        self.assertEqual(post.pub_date, None)

        post.publish()

        self.assertEqual(post.status, PostStatus.published)
        self.assertNotEqual(post.pub_date, None)

    def test_get_recent(self):
        post = self.create_post()
        self.assertEqual(len(Post.get_recent(1).items), 0)
        post.publish()
        self.assertEqual(len(Post.get_recent(1).items), 1)

    def test_get_published(self):
        post = self.create_post()
        self.assertEqual(len(Post.get_published().all()), 0)
        post.publish()
        self.assertEqual(len(Post.get_published().all()), 1)

    def test_is_published(self):
        post = Post(status=PostStatus.published)
        self.assertTrue(post.is_published)

    def test_url(self):
        post = Post(status=PostStatus.published, slug='test-post')
        self.assertEqual(post.url, None)
        post.pub_date = datetime.date(2012, 4, 3)
        self.assertEqual(post.url, '/blog/2012/04/03/test-post')

    def test_continue_url(self):
        post = Post(status=PostStatus.published, slug='test-post')
        self.assertEqual(post.continue_url, None)
        post.pub_date = datetime.date(2012, 4, 3)
        expected = '/blog/2012/04/03/test-post#{}'.format(
            self.app.config['POST_CONTINUE_LINK_FRAGMENT'])
        self.assertEqual(post.continue_url, expected)

    def test_preview(self):
        post = Post(body=u'test <!-- preview -->')
        self.assertEqual(post.preview, u'test...')

        post = Post(body=u'test ')
        self.assertEqual(post.preview, u'test')

    def test_tags(self):
        post = self.create_post(tags=[Tag('boeing'), Tag('airbus')])
        self.assertEqual(len(post.tags), 2)
        self.assertEqual(Tag.query.count(), 2)


class TagTests(EstherTestCase):
    def test_slug_generated_from_name(self):
        tag = Tag('train spotting')
        self.assertEqual(tag.slug, 'train-spotting')

    def test_url(self):
        tag = Tag('train spotting')
        self.assertEqual(tag.url, '/blog/tags/train-spotting')
