from datetime import datetime, timedelta

from flask import url_for
import pytz
from werkzeug.http import parse_cookie

from esther import db
from esther.models import utc_now, List, Item
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_auth import AuthMixin
from esther.views.todo import (CSRF_COOKIE_NAME, API_EMPTY_BODY_ERROR,
                               API_INVALID_PARAMETERS)


class TodoMixin(AuthMixin):
    def create_list(self, commit=True, **field_values):
        default_field_values = {
            'title': 'Upcoming Travel Plans',
            'description': 'Things I\'m doing next week',
        }
        default_field_values.update(field_values)

        if 'owner' not in default_field_values:
            default_field_values['owner'] = self.create_user(commit=False)

        todo_list = List(**default_field_values)

        db.session.add(todo_list)
        if commit:
            db.session.commit()

        return todo_list

    def create_item(self, commit=True, **field_values):
        default_field_values = {
            'content': 'Go to the store',
            'details': 'Publix in South Miami',
            'due': utc_now() + timedelta(hours=3)
        }
        default_field_values.update(field_values)

        if 'todo_list' not in field_values:
            default_field_values['todo_list'] = self.create_list(commit=False)

        item = Item(**default_field_values)

        db.session.add(item)
        if commit:
            db.session.commit()

        return item

    def assert_post_403(self):
        response = self.client.post(self.url, data=self.data)
        self.assert_403(response)


class FrontendTests(EstherDBTestCase, AuthMixin):
    def get_set_cookie_names(self, response):
        set_cookies = response.headers.getlist('Set-Cookie')
        return [parse_cookie(c).keys()[0] for c in set_cookies]

    def test_index_accessible(self):
        response = self.client.get('/todo')
        self.assert_template_used('todo/index.html')
        cookie_names = self.get_set_cookie_names(response)
        self.assertFalse(CSRF_COOKIE_NAME in cookie_names)

        # The CSRF token should be set for authenticated users
        self.login()
        response = self.client.get('/todo')
        cookie_names = self.get_set_cookie_names(response)
        self.assertTrue(CSRF_COOKIE_NAME in cookie_names)

        response = self.client.get('/todo')
        cookie_names = self.get_set_cookie_names(response)
        self.assertFalse(CSRF_COOKIE_NAME in cookie_names)


class ListsAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(ListsAPITests, self).setUp()
        self.user = self.create_user()
        self.url = url_for('todo.lists', owner_id=self.user.id)
        self.data = {'title': 'Some sort of title',
                     'description': 'This is a new list.'}

    def test_get_lists(self):
        todo_list1 = self.create_list(owner=self.user, commit=False)
        todo_list2 = self.create_list(title='My second list', owner=self.user,
                                      description='Nothing really here')
        response = self.client.get(self.url)
        self.assert_200(response)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['title'], todo_list1.title)
        self.assertEqual(response.json[1]['title'], todo_list2.title)

    def test_get_lists_private(self):
        self.create_list(owner=self.user, is_public=False)
        self.assertEqual(len(self.client.get(self.url).json), 0)
        self.login(user=self.user)
        self.assertEqual(len(self.client.get(self.url).json), 1)
        response = self.client.get(self.url)
        self.assertEqual(len(response.json), 1)

        # A logged in user should only be able to view private
        # lists that he or she owns
        another_user = self.create_user(email='danny@example.com')
        self.login(user=another_user)
        self.assertEqual(len(self.client.get(self.url).json), 0)

    def test_post(self):
        self.login(user=self.user)
        response = self.client.post(self.url, data=self.data)
        self.assert_status(response, 201)
        new_list = List.query.filter_by(title=self.data['title']).first()
        url = 'http://localhost/todo/api/{}/lists/{}'.format(self.user.id,
                                                             new_list.slug)
        self.assertEqual(response.headers['Location'], url)

    def test_post_as_another_user_fails(self):
        self.assert_post_403()
        another_user = self.create_user(email='jim@example.com')
        self.login(user=another_user)
        self.assert_post_403()

    def assert_invalid_title(self, modify_data=lambda d: None):
        self.login(user=self.user)
        response = self.client.post(self.url, data=self.data)
        self.assert_status(response, 201)
        modify_data(self.data)
        response = self.client.post(self.url, data=self.data)
        self.assert_status(response, 422)
        self.assertTrue(response.json['title'][0].startswith('Invalid title'))

    def test_post_with_duplicate_title_fails(self):
        self.assert_invalid_title()

    def test_post_with_duplicate_slug_fails(self):
        def modify_data(data):
            data['title'] = data['title'].upper()
        self.assert_invalid_title(modify_data)


class ListDetailAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(ListDetailAPITests, self).setUp()
        self.todo_list = self.create_list()
        self.url = url_for('todo.list_detail', owner_id=self.todo_list.owner.id,
                           slug=self.todo_list.slug)
        self.data = {'title': 'Another version of the title'}

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.json['id'], self.todo_list.id)
        self.assertEqual(response.json['title'], self.todo_list.title)
        self.todo_list.is_public = False
        db.session.commit()
        self.assert_404(self.client.get(self.url))

    def test_get_list_with_different_owner_id_fails(self):
        url = url_for('todo.list_detail', owner_id=999,
                      slug=self.todo_list.slug)
        self.assert_404(self.client.get(url))

    def test_patch(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data=self.data)
        self.assert_200(response)
        self.assertEqual(response.json['title'], self.data['title'])
        self.assertEqual(response.json['description'],
                         'Things I\'m doing next week')
        self.assertEqual(response.json['is_public'], True)

    def test_patching_private_list_does_not_leak_existence(self):
        self.todo_list.is_public = False
        db.session.commit()
        response = self.client.patch(self.url, data=self.data)
        self.assert_404(response)

    def test_patching_public_list_as_diff_user_fails(self):
        response = self.client.patch(self.url, data=self.data)
        self.assert_403(response)

    def test_patch_with_invalid_paremeters_fails(self):
        self.login(user=self.todo_list.owner)
        data = {'title': 'x' * 129}
        response = self.client.patch(self.url, data=data)
        self.assert_status(response, 422)

    def test_patch_with_empty_body_fails(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data={})
        self.assertEqual(response.json, API_EMPTY_BODY_ERROR)

    def test_patch_with_extraneous_parameters_fails(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data={'window': 'cleaner'})
        self.assertEqual(response.json, API_INVALID_PARAMETERS)


class ItemsAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(ItemsAPITests, self).setUp()
        self.user = self.create_user(commit=False)
        self.todo_list = self.create_list(owner=self.user)
        self.url = url_for('todo.items', owner_id=self.user.id,
                           list_slug=self.todo_list.slug)
        self.data = {
            'content': 'Buy four pieces of shrimp.',
            'details': 'Bottom shelf, aisle 12.',
            'due': 'Sat, 09 Mar 2013 10:15:39 GMT'
        }

    def create_items(self):
        self.first_item = self.create_item(todo_list=self.todo_list,
                                           commit=False)
        self.second_item = self.create_item(
            content='Eat at the place',
            todo_list=self.todo_list,
            due=self.first_item.due - timedelta(hours=2)
        )

    def test_get_items(self):
        self.create_items()
        response = self.client.get(self.url)
        self.assert_200(response)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['content'], 'Eat at the place')
        self.assertEqual(response.json[1]['content'], 'Go to the store')

    def test_get_items_private(self):
        self.todo_list.is_public = False
        db.session.commit()
        self.assert_404(self.client.get(self.url))

    def test_post(self):
        self.login(user=self.user)
        response = self.client.post(self.url, data=self.data)
        self.assert_status(response, 201)
        new_item = Item.query.filter_by(content=self.data['content']).first()
        self.assertEqual(new_item.details, 'Bottom shelf, aisle 12.')
        expected_due = datetime(2013, 3, 9, 10, 15, 39, tzinfo=pytz.utc)
        self.assertEqual(new_item.due, expected_due)
        url = 'http://localhost/todo/api/{}/lists/{}/items/{}'.format(
            self.user.id, self.todo_list.slug, new_item.id)
        self.assertEqual(response.headers['Location'], url)

    def test_post_as_another_user_fails(self):
        self.assert_post_403()
        another_user = self.create_user(email='jim@example.com')
        self.login(user=another_user)
        self.assert_post_403()

    def test_post_missing_fields_fails(self):
        self.login(user=self.user)
        del self.data['content']
        response = self.client.post(self.url, data=self.data)
        self.assert_status(response, 422)
        self.assertEqual(response.json['content'][0], 'This field is required.')


class ItemDetailAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(ItemDetailAPITests, self).setUp()
        self.item = self.create_item()
        self.todo_list = self.item.todo_list
        self.url = url_for(
            'todo.item_detail',
            owner_id=self.todo_list.owner.id,
            list_slug=self.todo_list.slug,
            item_id=self.item.id
        )
        self.data = {
            'content': 'Check if the bread is ready.',
            'details': 'Last time it wasn\t done on time.',
            'due': 'Sat, 01 Mar 2013 11:15:45 GMT',
            'is_done': True
        }

    def test_get_item(self):
        response = self.client.get(self.url)
        self.assertEqual(response.json['id'], self.item.id)
        self.assertEqual(response.json['content'], self.item.content)
        self.item.todo_list.is_public = False
        db.session.commit()
        self.assert_404(self.client.get(self.url))
        self.login(user=self.todo_list.owner)
        self.assert_200(self.client.get(self.url))

    def test_get_item_with_different_owner_id_fails(self):
        url = url_for('todo.item_detail', owner_id=self.todo_list.owner.id,
                      list_slug=self.todo_list.slug, item_id=999)
        self.assert_404(self.client.get(url))

    def test_get_item_with_different_list_slug_fails(self):
        url = url_for('todo.item_detail', owner_id=self.todo_list.owner.id,
                      list_slug='some-invalid-slug', item_id=self.item.id)
        self.assert_404(self.client.get(url))

    def test_patch(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data=self.data)
        self.assert_200(response)
        self.assertEqual(self.item.content, 'Check if the bread is ready.')
        self.assertEqual(self.item.details, 'Last time it wasn\t done on time.')
        self.assertEqual(self.item.is_done, True)

    def test_patching_private_item_does_not_leak_existence(self):
        self.todo_list.is_public = False
        db.session.commit()
        response = self.client.patch(self.url, data=self.data)
        self.assert_404(response)

    def test_patching_public_item_as_diff_user_fails(self):
        response = self.client.patch(self.url, data=self.data)
        self.assert_403(response)

    def test_patch_with_invalid_paremeters_fails(self):
        self.login(user=self.todo_list.owner)
        data = {'due': 'x' * 256}
        response = self.client.patch(self.url, data=data)
        self.assert_status(response, 422)

    def test_patch_with_empty_body_fails(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data={})
        self.assertEqual(response.json, API_EMPTY_BODY_ERROR)

    def test_patch_with_extraneous_parameters_fails(self):
        self.login(user=self.todo_list.owner)
        response = self.client.patch(self.url, data={'window': 'cleaner'})
        self.assertEqual(response.json, API_INVALID_PARAMETERS)
