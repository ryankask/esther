from esther.models import User
from esther.tests.helpers import EstherTestCase


class UserTests(EstherTestCase):
    def test_set_password(self):
        user = User('ryan@example.com', 'Ryan')
        user.set_password('password')
        self.assertNotEqual(user.password, 'password')
