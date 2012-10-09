from esther.models import User, get_columns
from esther.tests.helpers import EstherTestCase


class UtilityTests(EstherTestCase):
    def test_get_columns(self):
        expected = set(['id', 'email', 'full_name', 'short_name', 'password',
                        'is_active', 'is_admin'])
        self.assertEqual(set(get_columns(User)), expected)


class UserTests(EstherTestCase):
    def test_set_password(self):
        user = User('ryan@example.com', 'Ryan')
        user.set_password('password')
        self.assertNotEqual(user.password, 'password')
