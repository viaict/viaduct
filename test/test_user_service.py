import unittest

from unittest import mock
from unittest.mock import patch

from app.service import user_service

user_repository_mock = mock.MagicMock()


@patch.object(user_service, 'user_repository', user_repository_mock)
class TestAlvService(unittest.TestCase):

    def setUp(self):
        user_repository_mock.reset_mock()

    def test_find_by_id(self):
        user_id = 1
        user_repository_mock.find_by_id.return_value = user_id

        a = user_service.find_by_id(user_id)

        self.assertEqual(a, user_id)
        user_repository_mock.find_by_id.assert_called_once()
        user_repository_mock.find_by_id.assert_called_with(1)

    def test_find_members():
        user_service.find_members()

        user_repository_mock.find_members.assert_called_once()
