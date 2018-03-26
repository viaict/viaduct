import datetime
import unittest
from unittest.mock import patch, Mock, ANY

from app.enums import PimpyTaskStatus
from app.exceptions import ValidationException, ResourceNotFoundException, \
    InvalidMinuteException
from app.models.group import Group
from app.models.pimpy import Task
from app.models.user import User
from app.repository import pimpy_repository, group_repository, task_repository
from app.service import pimpy_service, group_service

pimpy_repository_mock = Mock(pimpy_repository)
group_repository_mock = Mock(group_repository)
task_repository_mock = Mock(task_repository)
pimpy_service_add_task_mock = Mock(pimpy_service._add_task)

task_mock = Mock(Task)
abc_task_mock = Mock(Task)
def_task_mock = Mock(Task)

group_mock = Mock(Group)

foo_user_mock = Mock(User)
foo_user_mock.configure_mock(first_name='Foo', last_name='Oof', name='Foo Oof')
bar_user_mock = Mock(User)
bar_user_mock.configure_mock(first_name='Bar', last_name='Rab', name='Bar Rab')

existing_minute_id = 45
existing_task_id = 10604  # ABC
existing_task_id2 = 13775  # DEF
existing_group_id = 20
nonexisting_group_id = 21
existing_task_name = 'existing task'
nonexisting_task_name = 'nonexisting task'
existing_user_name1 = 'Foo'
existing_user_name2 = 'Bar'
correct_date_range = (datetime.datetime.now() - datetime.timedelta(days=1),
                      datetime.datetime.now())

valid_minute = """
ACTIE Foo: Do something 1
ACTIE Foo,bar: Do something 2
ACTIES Foo,bar: Do something 3
DONE ABC
REMOVE DEF
"""
valid_minute_parse_response = \
    ([(1, "Do something 1", [foo_user_mock]),
      (2, "Do something 2", [foo_user_mock, bar_user_mock]),
      (3, "Do something 3", [foo_user_mock]),
      (3, "Do something 3", [bar_user_mock])],
     [(4, existing_task_id)],
     [(5, existing_task_id2)])

valid_minute_multiple_remove = """
REMOVE ABC, DEF
"""
valid_minute_multiple_remove_parse_response = \
    ([], [], [(1, existing_task_id), (1, existing_task_id2)])

valid_minute_multiple_done = """
DONE ABC, DEF
"""
valid_minute_multiple_done_parse_response = \
    ([], [(1, existing_task_id), (1, existing_task_id2)], [])

invalid_minute_no_colon_task = """
TASK Foo do something
ACTIE Bar do something
"""

invalid_minute_no_colon_task_error_response = \
    [(1, "TASK Foo do something"), (2, "ACTIE Bar do something")]

invalid_minute_no_b32_id = """
DONE #B5, %2G
"""
invalid_minute_no_b32_id_error_response = \
    [(1, "DONE #B5, %2G")]


def mock_find_group_id(group_id):
    if group_id == existing_group_id:
        return group_mock
    else:
        return None


group_repository_mock.find_by_id.side_effect = mock_find_group_id


def mock_get_list_of_users_from_string(group_id, value):
    if value.lower() == 'foo,bar' or value.lower().strip() == '':
        return [foo_user_mock, bar_user_mock]
    if value.lower() == 'foo':
        return [foo_user_mock]
    if value.lower() == 'bar':
        return [bar_user_mock]
    else:
        raise ValidationException("")


def mock_find_task_by_name_content_group(name, content, group):
    if name == existing_task_name:
        return Mock(spec=Task)
    else:
        return None


task_repository_mock.find_task_by_name_content_group.side_effect = \
    mock_find_task_by_name_content_group


def mock_parse_minute_into_tasks(content, group):
    if content == valid_minute:
        return valid_minute_parse_response
    if content == valid_minute_multiple_done:
        return valid_minute_multiple_done_parse_response
    if content == valid_minute_multiple_remove:
        return valid_minute_multiple_remove_parse_response
    if content == invalid_minute_no_colon_task:
        raise InvalidMinuteException(
            invalid_minute_no_colon_task_error_response)
    if content == invalid_minute_no_b32_id:
        raise InvalidMinuteException(
            invalid_minute_no_b32_id_error_response)


def mock_find_task_by_id(task_id):
    if task_id == existing_task_id:
        return abc_task_mock
    if task_id == existing_task_id2:
        return def_task_mock
    raise ResourceNotFoundException('task', task_id)


pimpy_repository_mock.find_task_by_id.side_effect = mock_find_task_by_id

task_mock.status_meanings = Task.status_meanings


# TODO: replace with the two arguments to reset_mock when we're using py 3.6
def reset_mock(mock):
    mock.reset_mock()
    mock.return_value = None
    mock.side_effect = None


@patch.object(group_service, 'group_repository', group_repository_mock)
@patch.object(pimpy_service, 'pimpy_repository', pimpy_repository_mock)
@patch.object(pimpy_service, 'task_repository', task_repository_mock)
@patch.object(pimpy_service, 'Task', task_mock)
class TestPimpyService(unittest.TestCase):
    def setUp(self):
        reset_mock(pimpy_repository_mock)
        reset_mock(group_repository_mock)
        reset_mock(task_repository_mock)
        reset_mock(group_mock)

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
        pimpy_service.get_all_minutes_for_group(
            existing_group_id, correct_date_range)
        pimpy_repository_mock.get_all_minutes_for_group. \
            assert_called_once_with(group_mock,
                                    correct_date_range)

    def test_get_all_minutes_for_group_not_found(self):
        group_repository_mock.find_by_id.return_value = None
        with self.assertRaises(ResourceNotFoundException):
            pimpy_service.get_all_minutes_for_group(
                nonexisting_group_id, correct_date_range)

    def test_check_date_range(self):
        today = datetime.datetime.now()
        date_range = [True, False, None]
        with self.assertRaises(ValidationException):
            pimpy_service.check_date_range(date_range)

        date_range = [today, True]
        with self.assertRaises(ValidationException):
            pimpy_service.check_date_range(date_range)

        date_range = (today, today - datetime.timedelta(days=1))
        with self.assertRaises(ValidationException):
            pimpy_service.check_date_range(date_range)

    def test_get_all_tasks_for_user(self):
        user = Mock(User)
        date_range = None

        # Without date_range
        pimpy_service.get_all_tasks_for_user(user, date_range)
        pimpy_repository_mock.get_all_tasks_for_user.assert_called_once_with(
            user, date_range)

        # With date_range.
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        today = datetime.datetime.now()
        date_range = (yesterday, today)
        reset_mock(pimpy_repository_mock)
        pimpy_service.get_all_tasks_for_user(user, date_range)
        pimpy_repository_mock.get_all_tasks_for_user.assert_called_once_with(
            user, date_range)

    def test_get_all_tasks_for_group(self):
        pimpy_service.get_all_tasks_for_group(existing_group_id)
        pimpy_repository_mock.get_all_tasks_for_group.assert_called_once_with(
            group_mock, None, None)

    def test_get_all_tasks_for_group_not_found(self):
        group_repository_mock.find_by_id.return_value = None
        with self.assertRaises(ResourceNotFoundException):
            pimpy_service.get_all_tasks_for_group(
                nonexisting_group_id, correct_date_range)

    def test_get_task_status_choices(self):
        actual = pimpy_service.get_task_status_choices()
        expected = [(0, 'Niet begonnen'), (1, 'Begonnen'), (2, 'Done'),
                    (3, 'Niet Done'), (4, 'Gecheckt'), (5, 'Verwijderd')]
        self.assertEqual(actual, expected)

    def test_get_list_of_users_from_string(self):
        group_mock.users.all.side_effect = lambda: [foo_user_mock,
                                                    bar_user_mock]

        users1 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'foo,bar')
        self.assertEqual(users1, [foo_user_mock, bar_user_mock])
        users2 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'foo, bar')
        self.assertEqual(users2, [foo_user_mock, bar_user_mock])
        users3 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'bar')
        self.assertEqual(users3, [bar_user_mock])
        users4 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'foo')
        self.assertEqual(users4, [foo_user_mock])

        users1 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'FOO,BAR')
        self.assertEqual(users1, [foo_user_mock, bar_user_mock])
        users2 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'FOO, BAR')
        self.assertEqual(users2, [foo_user_mock, bar_user_mock])
        users3 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'BAR')
        self.assertEqual(users3, [bar_user_mock])
        users4 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, 'FOO')
        self.assertEqual(users4, [foo_user_mock])

    def test_get_list_of_users_from_string_no_comma_sep_users(self):
        with self.assertRaises(ValidationException):
            pimpy_service.get_list_of_users_from_string(
                existing_group_id, None)

    def test_get_list_of_users_from_string_empty_string(self):
        users1 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, '')
        self.assertEqual(group_mock.users.all(), users1)

        users2 = pimpy_service.get_list_of_users_from_string(
            existing_group_id, '    ')
        self.assertEqual(group_mock.users.all(), users2)

    def test_get_list_of_users_from_string_user_not_found(self):
        with self.assertRaises(ValidationException):
            pimpy_service.get_list_of_users_from_string(
                existing_group_id, 'x')

        with self.assertRaises(ValidationException):
            pimpy_service.get_list_of_users_from_string(
                existing_group_id, 'foo,#,bar')

    def test_set_task_status(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)

        status = PimpyTaskStatus.NOT_STARTED.value
        mock_user.member_of_group.return_value = True

        pimpy_service.set_task_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_once_with(
            mock_task, status)

    def test_set_task_status_member_not_group_not_owner(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        mock_task.users = []

        status = PimpyTaskStatus.NOT_STARTED.value

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

        status = PimpyTaskStatus.NOT_STARTED.value

        mock_user.member_of_group.return_value = False

        pimpy_service.set_task_status(mock_user, mock_task, status)
        pimpy_repository_mock.update_status.assert_called_once_with(
            mock_task, status)

    def test_set_task_status_invalid_status(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        mock_task.users = [mock_user]

        status = PimpyTaskStatus.MAX.value + 1

        mock_user.member_of_group.return_value = False

        with self.assertRaises(ValidationException):
            pimpy_service.set_task_status(mock_user, mock_task, status)

    def test_add_task_by_user_string_invalid_group(self):
        with self.assertRaises(ResourceNotFoundException):
            pimpy_service.add_task_by_user_string('foo', 'content', -1,
                                                  nonexisting_group_id, 1,
                                                  existing_minute_id,
                                                  PimpyTaskStatus.NOT_STARTED)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_task_by_user_string_existing_task(self):
        with self.assertRaises(ValidationException):
            userlist = existing_user_name1 + ',' + existing_user_name2
            pimpy_service.add_task_by_user_string(
                existing_task_name, 'test content', existing_group_id,
                userlist, None, None, PimpyTaskStatus.NOT_STARTED.value)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_task_by_user_string_existing_task_in_minute(self):
        userlist = existing_user_name1 + ',' + existing_user_name2
        pimpy_service.add_task_by_user_string(
            existing_task_name, 'test content', existing_group_id,
            userlist, 1, existing_minute_id,
            PimpyTaskStatus.NOT_STARTED.value)

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_add_task_by_user_string_nonexisting_task(self):
        user_list = existing_user_name1 + ',' + existing_user_name2
        pimpy_service.add_task_by_user_string(
            nonexisting_task_name, 'test content', existing_group_id,
            user_list, 1, existing_minute_id,
            PimpyTaskStatus.NOT_STARTED.value)

    @patch.object(pimpy_service, '_parse_minute_into_tasks',
                  mock_parse_minute_into_tasks)
    @patch.object(pimpy_service, '_add_task', pimpy_service_add_task_mock)
    def test_add_minute(self):
        date = datetime.datetime.today()
        pimpy_service.add_minute(valid_minute, date, group_mock)
        pimpy_repository_mock.add_minute.assert_called_once_with(
            content=valid_minute, date=date, group=group_mock)
        pimpy_service_add_task_mock.assert_any_call(
            'Do something 1', '', group_mock,
            [foo_user_mock], 1, ANY, 0)
        pimpy_service_add_task_mock.assert_any_call(
            'Do something 2', '', group_mock,
            [foo_user_mock, bar_user_mock], 2, ANY, 0)
        pimpy_service_add_task_mock.assert_any_call(
            'Do something 3', '', group_mock, [foo_user_mock], 3, ANY, 0)
        pimpy_service_add_task_mock.assert_any_call(
            'Do something 3', '', group_mock, [bar_user_mock], 3, ANY, 0)

        pimpy_repository_mock.find_task_by_id.assert_any_call(
            existing_task_id)
        pimpy_repository_mock.find_task_by_id.assert_any_call(
            existing_task_id2)
        pimpy_repository_mock.update_status.assert_any_call(abc_task_mock, 4)
        pimpy_repository_mock.update_status.assert_any_call(def_task_mock, 5)

    @patch.object(pimpy_service, '_parse_minute_into_tasks',
                  mock_parse_minute_into_tasks)
    def test_add_minute_invalid(self):
        date = datetime.datetime.today()
        with self.assertRaises(InvalidMinuteException):
            pimpy_service.add_minute(invalid_minute_no_colon_task,
                                     date, group_mock)
        with self.assertRaises(InvalidMinuteException):
            pimpy_service.add_minute(invalid_minute_no_b32_id,
                                     date, group_mock)

    def test_edit_task_property_content(self):
        value = 'val'
        pimpy_service.edit_task_property(Mock(User), existing_task_id,
                                         content=value)

        pimpy_repository_mock.edit_task_content.assert_called_once_with(
            abc_task_mock, value)

    def test_edit_task_property_title(self):
        value = 'val'

        pimpy_service.edit_task_property(Mock(User), existing_task_id,
                                         title=value)

        pimpy_repository_mock.edit_task_title.assert_called_once_with(
            abc_task_mock, value)

    def test_edit_task_users(self):
        mock_user = Mock(User)

        with patch.object(pimpy_service, 'get_list_of_users_from_string',
                          lambda group_id, userlist: [mock_user]):
            pimpy_service.edit_task_property(
                mock_user, existing_task_id, users_property=[mock_user])
            pimpy_repository_mock.edit_task_users.assert_called_once_with(
                abc_task_mock, [mock_user])

    def test_edit_task_property_invalid_group(self):
        mock_user = Mock(User)
        mock_task = Mock(Task)
        pimpy_repository_mock.find_task_by_id.return_value = mock_task

        mock_user.member_of_group = Mock(return_value=False)

        with self.assertRaises(ValidationException):
            pimpy_service.edit_task_property(
                mock_user, existing_task_id, content='val')

    @patch.object(pimpy_service, 'get_list_of_users_from_string',
                  mock_get_list_of_users_from_string)
    def test_parse_minute_into_tasks(self):
        self.assertEqual(pimpy_service._parse_minute_into_tasks(
            valid_minute, group_mock), valid_minute_parse_response)
        self.assertEqual(pimpy_service._parse_minute_into_tasks(
            valid_minute_multiple_remove, group_mock),
            valid_minute_multiple_remove_parse_response)
        self.assertEqual(pimpy_service._parse_minute_into_tasks(
            valid_minute_multiple_done, group_mock),
            valid_minute_multiple_done_parse_response)

        with self.assertRaises(InvalidMinuteException) as e1:
            pimpy_service._parse_minute_into_tasks(
                invalid_minute_no_b32_id, group_mock)
        self.assertEqual(invalid_minute_no_b32_id_error_response,
                         e1.exception.details)
        with self.assertRaises(InvalidMinuteException) as e2:
            pimpy_service._parse_minute_into_tasks(
                invalid_minute_no_colon_task, group_mock)
        self.assertEqual(invalid_minute_no_colon_task_error_response,
                         e2.exception.details)
