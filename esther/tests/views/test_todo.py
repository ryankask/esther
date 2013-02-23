from flask import url_for

from esther import db
from esther.models import List
from esther.tests.helpers import EstherDBTestCase
from esther.tests.views.test_auth import AuthMixin


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


class ListAPITests(EstherDBTestCase, TodoMixin):
    def setUp(self):
        super(ListAPITests, self).setUp()
        self.user = self.create_user()
        self.url = url_for('todo.lists', owner_id=self.user.id)

    def test_get_lists(self):
        todo_list1 = self.create_list(owner=self.user, commit=False)
        todo_list2 = self.create_list(title='My second list', owner=self.user,
                                      description='Nothing really here')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
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
