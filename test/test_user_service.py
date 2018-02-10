import unittest
from unittest.mock import patch, MagicMock

import bcrypt

from app.exceptions import ResourceNotFoundException, AuthorizationException, \
    ValidationException
from app.models.user import User
from app.repository import user_repository
from app.service import user_service

user_repository_mock = MagicMock(spec=dir(user_repository))


@patch.object(user_service, 'user_repository', user_repository_mock)
class TestUserService(unittest.TestCase):

    def setUp(self):
        user_repository_mock.reset_mock()

    def test_set_password(self):
        user = MagicMock()
        password = "password"
        user_repository_mock.find_by_id.return_value = user

        u = user_service.set_password(1, password)

        self.assertEqual(u, user)
        user_repository_mock.find_by_id.assert_called_once_with(1)
        self.assertNotEqual(u.password, password)

    def test_find_by_id(self):
        user_id = 1
        user_repository_mock.find_by_id.return_value = user_id

        a = user_service.find_by_id(user_id)

        self.assertEqual(a, user_id)
        user_repository_mock.find_by_id.assert_called_once_with(1)

    def test_get_user_by_id(self):
        user_id = 1
        user_repository_mock.find_by_id.return_value = user_id

        a = user_service.get_user_by_id(user_id)

        self.assertEqual(a, user_id)
        user_repository_mock.find_by_id.assert_called_once_with(1)

    def test_get_user_by_id_not_found(self):
        user_repository_mock.find_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            user_service.get_user_by_id(1)

        user_repository_mock.find_by_id.assert_called_once_with(1)

    def test_get_user_by_email(self):
        email = "test@svia.nl"
        user_repository_mock.find_user_by_email.return_value = email

        e = user_service.get_user_by_email(email)

        self.assertEqual(e, email)
        user_repository_mock.find_user_by_email.assert_called_once_with(email)

    def test_get_user_by_email_not_found(self):
        email = "test@svia.nl"
        user_repository_mock.find_user_by_email.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            user_service.get_user_by_email(email)

        user_repository_mock.find_user_by_email.assert_called_once_with(email)

    def test_find_members(self):
        user_service.find_members()

        user_repository_mock.find_members.assert_called_once()

    def test_get_user_by_login(self):
        email = "test@svia.nl"
        password = "password"

        expected_user = MagicMock(spec=dir(User))
        expected_user.disabled = False
        expected_user.password = bcrypt.hashpw(password, bcrypt.gensalt())

        user_repository_mock.find_user_by_email.return_value = expected_user

        actual_user = user_service.get_user_by_login(email, password)

        self.assertEqual(expected_user, actual_user)

    def test_get_user_by_login_user_not_found(self):
        email = "test@svia.nl"
        password = "password"

        user_repository_mock.find_user_by_email.return_value = None
        with self.assertRaises(ResourceNotFoundException):
            user_service.get_user_by_login(email, password)

    def test_get_user_by_login_user_disabled(self):
        email = "test@svia.nl"
        password = "password"

        expected_user = MagicMock(spec=dir(User))
        expected_user.disabled = True

        user_repository_mock.find_user_by_email.return_value = expected_user

        with self.assertRaises(AuthorizationException):
            user_service.get_user_by_login(email, password)

    def test_get_user_by_login_wrong_password(self):
        email = "test@svia.nl"
        password = "password"
        wrong_password = "wrong_password"

        expected_user = MagicMock(spec=dir(User))
        expected_user.disabled = False
        expected_user.password = bcrypt.hashpw(password, bcrypt.gensalt())

        user_repository_mock.find_user_by_email.return_value = expected_user
        with self.assertRaises(ValidationException):
            user_service.get_user_by_login(email, wrong_password)
