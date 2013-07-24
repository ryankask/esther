from werkzeug.datastructures import MultiDict

from esther import db
from esther.forms import PostForm
from esther.models import PostStatus, Post, Tag
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_blog import BlogMixin


class PostFormTests(EstherDBTestCase, BlogMixin):
    form_data = MultiDict({
        'title': 'My Second Post', 'slug': 'my-first-post',
        'status': PostStatus.draft.value, 'body': 'Welcome'
    })

    def test_used_slug_raises_validation_error(self):
        self.create_post(self.create_user(commit=False))
        form = PostForm(self.form_data)
        self.assertFalse(form.validate())
        self.assertEqual(form.errors['slug'], [u'Slug is not unique.'])

    def test_comma_separated_tag_value_serialized_to_tag_objects(self):
        original_green_tag = Tag('green')
        db.session.add(original_green_tag)
        db.session.commit()

        self.form_data['tags'] = 'green, red, red, blue'
        form = PostForm(self.form_data)
        self.assertTrue(form.validate())
        self.assertEqual(len(form.tags.data), 3)

        tags = form.tags.data
        self.assertEqual(tags[0], original_green_tag)
        self.assertEqual(tags[1].id, None)
        self.assertEqual(tags[2].id, None)

    def test_empty_tags_value_creates_empty_set(self):
        self.form_data['tags'] = ''
        form = PostForm(self.form_data)
        self.assertTrue(form.validate())
        self.assertEqual(len(form.tags.data), 0)

    def test_blank_values_not_considered_tags(self):
        self.form_data['tags'] = ', pink, ,'
        form = PostForm(self.form_data)
        self.assertTrue(form.validate())
        self.assertEqual(len(form.tags.data), 1)

    def test_tag_name_ordering_preserved(self):
        self.form_data['tags'] = 'blue, green, blue, red'
        form = PostForm(self.form_data)
        self.assertTrue(form.validate())
        self.assertEqual(len(form.tags.data), 3)
        self.assertEqual(form.tags.data[0].name, 'blue')
        self.assertEqual(form.tags.data[1].name, 'green')
        self.assertEqual(form.tags.data[2].name, 'red')

    def test_post_tags_converted_to_comma_separated_string(self):
        post = Post(tags=[Tag('green'), Tag('blue')])
        form = PostForm(obj=post)
        self.assertEqual(form.tags._value(), 'green, blue')
