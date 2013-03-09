from datetime import timedelta

from flask import url_for

from esther import db
from esther.models import utc_now, List, Item
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_auth import AuthMixin
from esther.views.todo import API_EMPTY_BODY_ERROR, API_INVALID_PARAMETERS


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
        response = self.client.post(self.url, data=self.data)
        self.assert_403(response)
        another_user = self.create_user(email='jim@example.com')
        self.login(user=another_user)
        response = self.client.post(self.url, data=self.data)
        self.assert_403(response)

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


class SingleListAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(SingleListAPITests, self).setUp()
        self.todo_list = self.create_list()
        self.url = url_for('todo.list_', owner_id=self.todo_list.owner.id,
                           slug=self.todo_list.slug)
        self.data = {'title': 'Another version of the title'}

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.json['id'], self.todo_list.id)
        self.assertEqual(response.json['title'], self.todo_list.title)
        self.todo_list.is_public = False
        db.session.commit()
        self.assert_404(self.client.get(self.url))

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
        self.first_item = self.create_item(commit=False)
        self.todo_list = self.first_item.todo_list
        self.second_item = self.create_item(
            content='Eat at the place',
            todo_list=self.todo_list,
            due=self.first_item.due - timedelta(hours=2)
        )
        self.url = url_for('todo.items', owner_id=self.todo_list.owner.id,
                           list_slug=self.todo_list.slug)

    def test_get_items(self):
        response = self.client.get(self.url)
        self.assert_200(response)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['content'], 'Eat at the place')
        self.assertEqual(response.json[1]['content'], 'Go to the store')

    def test_get_items_private(self):
        self.todo_list.is_public = False
        db.session.commit()
        self.assert_404(self.client.get(self.url))
