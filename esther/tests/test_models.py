from esther import db
from esther.models import User, Post, PostStatus
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
    def test_publish(self):
        user = User(email='ryan@example.com', short_name='Ryan')
        db.session.add(user)

        post = Post(author=user, title='First Tiger on the Moon',
                    slug='first-tiger-moon', body='The contents.')
        db.session.add(post)

        db.session.commit()

        self.assertEqual(post.status, PostStatus.draft)
        self.assertEqual(post.pub_date, None)

        post.publish()

        self.assertEqual(post.status, PostStatus.published)
        self.assertNotEqual(post.pub_date, None)
