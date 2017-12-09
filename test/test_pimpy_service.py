import unittest
from unittest.mock import patch, Mock

from app.exceptions import ValidationException
from app.models.group import Group
from app.models.pimpy import Task
from app.models.user import User
from app.repository import pimpy_repository, group_repository, task_repository
from app.service import pimpy_service

pimpy_repository_mock = Mock(pimpy_repository)
group_repository_mock = Mock(group_repository)
task_repository_mock = Mock(task_repository)

existing_minute_id = 45
existing_task_id = 22
existing_group_id = 20
nonexisting_group_id = 21
existing_task_name = 'existing task'
nonexisting_task_name = 'nonexisting task'
existing_user_name1 = 'Foo'
existing_user_name2 = 'Bar'


def mock_find_group_id(group_id):
    if group_id == existing_group_id:
        return Mock(spec=Group)
    else:
        return None


# todo: properly mock this method by mocking the methods it calls.
def mock_get_list_of_users_from_string(group_id, value):
    if value.lower() == 'foo,bar':
        return [
            Mock(spec=User, first_name='Foo'),
            Mock(spec=User, first_name='Bar')
        ]
    else:
        raise ValidationException()


def mock_find_task_by_name_content_group(name, content, group):
    if name == existing_task_name:
        return Mock(spec=Task)
    else:
        return None


group_repository_mock.find_group_by_id.side_effect = mock_find_group_id

task_repository_mock.find_task_by_name_content_group.side_effect = \
    mock_find_task_by_name_content_group


@patch.object(pimpy_service, 'pimpy_repository', pimpy_repository_mock)
@patch.object(pimpy_service, 'group_repository', group_repository_mock)
@patch.object(pimpy_service, 'task_repository', task_repository_mock)
@patch.object(pimpy_service, 'Task', Mock(spec=Task))
class TestPimpyService(unittest.TestCase):
    def setUp(self):
        pass

    def test_find_minute_by_id(self):
        pimpy_service.find_minute_by_id(existing_minute_id)
        pimpy_repository_mock.find_minute_by_id.assert_called_with(
            existing_minute_id)

    def test_find_task_by_id(self):
        pimpy_service.find_task_by_id(existing_task_id)
        pimpy_repository_mock.find_task_by_id.assert_called_with(
            existing_task_id)

    def test_get_all_minutes_for_user(self):
        mock_user = Mock()
        pimpy_service.get_all_minutes_for_user(mock_user)
        pimpy_repository_mock.get_all_minutes_for_user.assert_called_with(
            mock_user)

    def test_get_all_minutes_for_group(self):
        pimpy_service.get_all_minutes_for_group(existing_group_id, (1, 2))
        pimpy_repository_mock.get_all_minutes_for_group.assert_called_with(
            existing_group_id, (1, 2))

    def test_get_all_tasks_for_groups(self):
        pimpy_service.get_all_tasks_for_groups([existing_group_id], (1, 2))
        pimpy_repository_mock.get_all_tasks_for_groups.assert_called_with(
            [existing_group_id], (1, 2), None)

    def test_update_status(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)

        status = 0

        pimpy_service.update_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_with(
            mock_task, status)

        with self.assertRaises(ValidationException):
            mock_user.member_of_group.return_value = False
            res = pimpy_service.update_status(mock_user, mock_task, status)
            self.assertFalse(res)
            pimpy_repository_mock.update_status.assert_not_called()

    def test_add_task_invalid_group(self):
        with self.assertRaises(ValidationException):
            pimpy_service.add_task('foo', 'content', -1, nonexisting_group_id,
                                   1, existing_minute_id, 0)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_existing_task(self):
        with self.assertRaises(ValidationException):
            userlist = existing_user_name1 + ',' + existing_user_name2
            pimpy_service.add_task(
                existing_task_name, 'test content', existing_group_id,
                userlist, 1, existing_minute_id, 0)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_nonexisting_task(self):
        userlist = existing_user_name1 + ',' + existing_user_name2
        pimpy_service.add_task(
            nonexisting_task_name, 'test content', existing_group_id,
            userlist, 1, existing_minute_id, 0)

    def test_edit_task_property(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)

        pimpy_repository_mock.find_task_by_id.return_value = mock_task

        value = 'val'

        self._test_edit_task_property_with_type(
            mock_user, mock_task, existing_task_id, 'content', value, value,
            pimpy_repository_mock.edit_task_content)

        self._test_edit_task_property_with_type(
            mock_user, mock_task, existing_task_id, 'title', value, value,
            pimpy_repository_mock.edit_task_title)

        with patch.object(pimpy_service, 'get_list_of_users_from_string',
                          lambda group_id, userlist: [mock_user]):
            self._test_edit_task_property_with_type(
                mock_user, mock_task, existing_task_id, 'users', value,
                [mock_user], pimpy_repository_mock.edit_task_users)

    def _test_edit_task_property_with_type(
            self, user, task, task_id, content, value, resvalue, func):
        pimpy_service.edit_task_property(
            user, task_id, content, value)
        func.assert_called_with(task, resvalue)

    def test_edit_task_property_invalid_group(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task

        mock_user.member_of_group = Mock(return_value=False)

        with self.assertRaises(ValidationException):
            pimpy_service.edit_task_property(
                mock_user, existing_task_id, 'content', 'val')
