from esther import db
from esther.models import User
from esther.tests.helpers import EstherDBTestCase
from esther.utils import add_user


class AddUserCommandTests(EstherDBTestCase):
    def test_add_user(self):
        add_user('ryan@example.com', 'Ryan')
        user = User.query.filter_by(email='ryan@example.com').first()
        self.assertEqual(user.short_name, 'Ryan')
        self.assertEqual(user.full_name, None)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.password, None)
        self.assertEqual(user.is_admin, False)

    def test_add_user_with_extra_fields(self):
        add_user('ryan@example.com', 'Ryan', is_admin=True, full_name='Ryan K')
        user = User.query.filter_by(email='ryan@example.com').first()
        self.assertEqual(user.is_admin, True)
        self.assertEqual(user.full_name, 'Ryan K')

    def test_non_column_keyword_args_not_set_as_attributes(self):
        user = add_user('ryan@example.com', 'Ryan', dummy=True)
        self.assertEqual(hasattr(user, 'dummy'), False)

    def test_late_commit(self):
        user = add_user('ryan@example.com', 'Ryan', commit=False)

        found_user = User.query.filter_by(email='ryan@example.com').first()
        self.assertEqual(found_user, None)

        user.is_admin = True
        db.session.commit()
        found_user = User.query.filter_by(email='ryan@example.com').first()
        self.assertEqual(found_user.is_admin, True)
