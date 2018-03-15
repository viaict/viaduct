import unittest
from unittest.mock import patch, Mock

from app.exceptions import ValidationException, ResourceNotFoundException
from app.models.group import Group
from app.models.pimpy import Task
from app.models.user import User
from app.repository import pimpy_repository, group_repository, task_repository
from app.service import pimpy_service

pimpy_repository_mock = Mock(pimpy_repository)
group_repository_mock = Mock(group_repository)
task_repository_mock = Mock(task_repository)
task_mock = Mock(Task)

existing_minute_id = 45
existing_task_id = 22
existing_group_id = 20
nonexisting_group_id = 21
existing_task_name = 'existing task'
nonexisting_task_name = 'nonexisting task'
existing_user_name1 = 'Foo'
existing_user_name2 = 'Bar'

group_repository_mock_mock = Mock(spec=Group)


def mock_find_group_id(group_id):
    if group_id == existing_group_id:
        return group_repository_mock_mock
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
        raise ValidationException("")


def mock_find_task_by_name_content_group(name, content, group):
    if name == existing_task_name:
        return Mock(spec=Task)
    else:
        return None


group_repository_mock.find_by_id.side_effect = mock_find_group_id

task_repository_mock.find_task_by_name_content_group.side_effect = \
    mock_find_task_by_name_content_group

task_mock.STATUS_NOT_STARTED = Task.STATUS_NOT_STARTED
task_mock.STATUS_STARTED = Task.STATUS_STARTED
task_mock.STATUS_DONE = Task.STATUS_DONE
task_mock.STATUS_NOT_DONE = Task.STATUS_NOT_DONE
task_mock.STATUS_CHECKED = Task.STATUS_CHECKED
task_mock.STATUS_DELETED = Task.STATUS_DELETED
task_mock.STATUS_MAX = Task.STATUS_MAX


# TODO: replace with the two argumennts to reset_mock when we're using py 3.6
def reset_mock(mock):
    mock.reset_mock()
    mock.return_value = None
    mock.side_effect = None


@patch.object(pimpy_service, 'pimpy_repository', pimpy_repository_mock)
@patch.object(pimpy_service, 'group_repository', group_repository_mock)
@patch.object(pimpy_service, 'task_repository', task_repository_mock)
@patch.object(pimpy_service, 'Task', task_mock)
class TestPimpyService(unittest.TestCase):
    def setUp(self):
        reset_mock(pimpy_repository_mock)
        reset_mock(group_repository_mock)
        reset_mock(task_repository_mock)

    def test_find_minute_by_id(self):
        pimpy_service.find_minute_by_id(existing_minute_id)
        pimpy_repository_mock.find_minute_by_id.assert_called_once_with(
            existing_minute_id)

    def test_find_task_by_id(self):
        pimpy_service.find_task_by_id(existing_task_id)
        pimpy_repository_mock.find_task_by_id.assert_called_once_with(
            existing_task_id)

    def test_get_all_minutes_for_user(self):
        mock_user = Mock()
        pimpy_service.get_all_minutes_for_user(mock_user)
        pimpy_repository_mock.get_all_minutes_for_user.assert_called_once_with(
            mock_user)

    def test_get_all_minutes_for_group(self):
        pimpy_service.get_all_minutes_for_group(existing_group_id, (1, 2))
        pimpy_repository_mock.get_all_minutes_for_group. \
            assert_called_once_with(group_repository_mock_mock, (1, 2))

    def test_set_task_status(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)

        status = Task.STATUS_NOT_STARTED
        mock_user.member_of_group.return_value = True

        pimpy_service.set_task_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_once_with(
            mock_task, status)

    def test_set_task_status_member_not_group_not_owner(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        mock_task.users = []

        status = Task.STATUS_NOT_STARTED

        pimpy_service.set_task_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_once_with(
            mock_task, status)

        with self.assertRaises(ValidationException):
            mock_user.member_of_group.return_value = False
            pimpy_service.set_task_status(mock_user, mock_task, status)
            pimpy_repository_mock.update_status.assert_not_called()

    def test_set_task_status_not_group_but_owner(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        mock_task.users = [mock_user]

        status = Task.STATUS_NOT_STARTED

        mock_user.member_of_group.return_value = False

        pimpy_service.set_task_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_once_with(
            mock_task, status)

    def test_add_task_invalid_group(self):
        with self.assertRaises(ResourceNotFoundException):
            pimpy_service.add_task_by_user_string('foo', 'content', -1,
                                                  nonexisting_group_id, 1,
                                                  existing_minute_id,
                                                  Task.STATUS_NOT_STARTED)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_existing_task(self):
        with self.assertRaises(ValidationException):
            userlist = existing_user_name1 + ',' + existing_user_name2
            pimpy_service.add_task_by_user_string(
                existing_task_name, 'test content', existing_group_id,
                userlist, 1, existing_minute_id,
                Task.STATUS_NOT_STARTED)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_nonexisting_task(self):
        user_list = existing_user_name1 + ',' + existing_user_name2
        pimpy_service.add_task_by_user_string(
            nonexisting_task_name, 'test content', existing_group_id,
            user_list, 1, existing_minute_id,
            Task.STATUS_NOT_STARTED)

    def test_edit_task_property_content(self):
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task
        value = 'val'

        pimpy_service.edit_task_property(Mock(User), existing_task_id,
                                         content=value)

        pimpy_repository_mock.edit_task_content.assert_called_once_with(
            mock_task, value
        )

    def test_edit_task_property_title(self):
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task
        value = 'val'

        pimpy_service.edit_task_property(Mock(User), existing_task_id,
                                         title=value)

        pimpy_repository_mock.edit_task_title.assert_called_once_with(
            mock_task, value
        )

    def _test_edit_task_property_with_type(
            self, content, func):
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task
        value = 'val'
        pimpy_service.edit_task_property(
            Mock(User), existing_task_id, content, value)
        if func:
            func.assert_called_once_with(mock_task, value)

    def test_edit_task_users(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task

        with patch.object(pimpy_service, 'get_list_of_users_from_string',
                          lambda group_id, userlist: [mock_user]):
            pimpy_service.edit_task_property(
                mock_user, existing_task_id, users_property=[mock_user])
            pimpy_repository_mock.edit_task_users.assert_called_once_with(
                mock_task, [mock_user])

    def test_edit_task_property_invalid_group(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task

        mock_user.member_of_group = Mock(return_value=False)

        with self.assertRaises(ValidationException):
            pimpy_service.edit_task_property(
                mock_user, existing_task_id, content='val')
