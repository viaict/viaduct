import unittest
from unittest.mock import patch, MagicMock

import bcrypt
from io import StringIO

from app.exceptions import ResourceNotFoundException, AuthorizationException, \
    ValidationException
from app.models.user import User
from app.models.file import File
from app.repository import user_repository
from app.service import user_service, file_service
from app.enums import FileCategory

user_repository_mock = MagicMock(spec=dir(user_repository))
file_service_mock = MagicMock(spec=dir(file_service))

avatar_file_data = StringIO('fake avatar file data')
avatar_file_data.filename = 'avatar.png'


@patch.object(user_service, 'user_repository', user_repository_mock)
@patch.object(user_service, 'file_service', file_service_mock)
class TestUserService(unittest.TestCase):

    def setUp(self):
        user_repository_mock.reset_mock()
        file_service_mock.reset_mock()

    def test_set_password(self):
        user = MagicMock()
        password = "password"
        user_repository_mock.find_by_id.return_value = user

        u = user_service.set_password(1, password)

        self.assertEqual(u, user)
        user_repository_mock.find_by_id.assert_called_once_with(1)
        self.assertNotEqual(u.password, password)
        user_repository_mock.save.assert_called_once_with(user)

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

    def test_user_has_avatar(self):
        user_id = 1
        avatar_file_id = 1

        user = MagicMock(spec=dir(User))

        user.id = user_id
        user.avatar_file_id = avatar_file_id

        user_repository_mock.find_by_id.return_value = user

        has_avatar = user_service.user_has_avatar(user_id)

        self.assertEqual(has_avatar, True)

    def test_user_has_no_avatar(self):
        user_id = 1
        avatar_file_id = None

        user = MagicMock(spec=dir(User))

        user.id = user_id
        user.avatar_file_id = avatar_file_id

        user_repository_mock.find_by_id.return_value = user

        has_avatar = user_service.user_has_avatar(user_id)

        self.assertEqual(has_avatar, False)

    def test_user_set_new_avatar(self):
        user_id = 1
        avatar_file_id = 1

        user = MagicMock(spec=dir(User))
        expected_avatar = MagicMock(spec=dir(File))

        user.id = user_id
        user.avatar_file_id = None
        expected_avatar.id = avatar_file_id

        user_repository_mock.find_by_id.return_value = user
        file_service_mock.add_file.return_value = expected_avatar

        user_service.set_avatar(user_id, avatar_file_data)

        self.assertEqual(user.avatar_file_id, avatar_file_id)
        file_service_mock.add_file.assert_called_once_with(
            FileCategory.USER_AVATAR,
            avatar_file_data, avatar_file_data.filename)

        file_service_mock.get_file_by_id.assert_not_called()
        file_service_mock.delete_file.assert_not_called()
        user_repository_mock.save.assert_called_once_with(user)

    def test_user_replace_avatar(self):
        user_id = 1
        old_avatar_file_id = 1
        new_avatar_file_id = 2

        user = MagicMock(spec=dir(User))
        old_avatar = MagicMock(spec=dir(File))
        expected_avatar = MagicMock(spec=dir(File))

        user.id = user_id
        user.avatar_file_id = old_avatar_file_id
        old_avatar.id = old_avatar_file_id
        expected_avatar.id = new_avatar_file_id

        user_repository_mock.find_by_id.return_value = user
        file_service_mock.add_file.return_value = expected_avatar
        file_service_mock.get_file_by_id.return_value = old_avatar

        user_service.set_avatar(user_id, avatar_file_data)

        self.assertEqual(user.avatar_file_id, new_avatar_file_id)

        file_service_mock.add_file.assert_called_once_with(
            FileCategory.USER_AVATAR,
            avatar_file_data, avatar_file_data.filename)

        file_service_mock.get_file_by_id.assert_called_once_with(
            old_avatar_file_id)
        file_service_mock.delete_file.assert_called_once_with(old_avatar)
        user_repository_mock.save.assert_called_once_with(user)

    def test_user_remove_avatar(self):
        user_id = 1
        avatar_file_id = 1

        user = MagicMock(spec=dir(User))
        avatar = MagicMock(spec=dir(File))

        user.id = user_id
        user.avatar_file_id = avatar_file_id
        avatar.id = avatar_file_id

        user_repository_mock.find_by_id.return_value = user
        file_service_mock.get_file_by_id.return_value = avatar

        user_service.remove_avatar(user_id)

        self.assertEqual(user.avatar_file_id, None)

        file_service_mock.get_file_by_id.assert_called_once_with(
            avatar_file_id)
        file_service_mock.delete_file.assert_called_once_with(avatar)
        user_repository_mock.save.assert_called_once_with(user)
