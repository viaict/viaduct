import unittest

from unittest.mock import patch, MagicMock

from app.service import user_service
from app.exceptions import ResourceNotFoundException

user_repository_mock = MagicMock()


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
