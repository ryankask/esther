from xml.etree import cElementTree

from esther.models import PostStatus
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_blog import BlogMixin


class BlogFeedTests(EstherDBTestCase, BlogMixin):
    def test_rss2_feed(self):
        user = self.create_user(commit=False)
        self.create_post(user, status=PostStatus.published, commit=False)
        self.create_post(user, title='Just another post',
                         slug='just-another-post', status=PostStatus.published)

        response = self.client.get('/feeds/blog')
        self.assert_200(response)
        self.assertEqual(response.mimetype, 'application/rss+xml')

        feed_config = self.app.config['FEEDS_CONFIG']['blog']

        channel = cElementTree.fromstring(response.data)[0]
        self.assertEqual(channel.find('title').text, feed_config['title'])
        self.assertEqual(channel.find('webMaster').text,
                         feed_config['webmaster'])
        self.assertEqual(channel.find('description').text,
                         feed_config['description'])
        self.assertEqual(len(channel.findall('item')), 2)
