from werkzeug.datastructures import MultiDict

from esther.forms import PostForm
from esther.models import PostStatus
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_blog import BlogMixin


class PostFormTests(EstherDBTestCase, BlogMixin):
    def test_used_slug_raises_validation_error(self):
        post = self.create_post(self.create_user(commit=False))
        form_data = MultiDict({'title': 'My Second Post', 'slug': post.slug,
                               'status': PostStatus.draft, 'body': 'Welcome'})
        form = PostForm(form_data)
        self.assertFalse(form.validate())
        self.assertEqual(form.errors['slug'], [u'Slug is not unique.'])
