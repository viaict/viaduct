import datetime
import re

import baas32 as b32
from fuzzywuzzy import fuzz

from app.enums import PimpyTaskStatus
from app.exceptions import ValidationException, InvalidMinuteException
from app.models.pimpy import Task
from app.repository import pimpy_repository, task_repository
from app.service import group_service

"""
What is pimpy?

Pimpy; Precise Inscriptions of Minutes with Python.
The minute system of the study association via.

Pimpy is used for handling the minutes and tasks of different groups.
By using different keywords in the minutes tasks are extracted and
automatically created.

The Minute(s) are the notes of a meeting where the written text is in.
With actions in these notes new Task(s) are created. These are bound to users,
and have a status.


"""
TASK_REGEX = re.compile(r"\s*(?:ACTIE|TASK)\s+(.*):\s*(.*)\s*$")
TASKS_REGEX = re.compile(r"\s*(?:ACTIES|TASKS)\s+(.*):\s*(.*)\s*$")
DONE_REGEX = re.compile("\s*(?:DONE) ([^\n\r]*)")
REMOVE_REGEX = re.compile("\s*(?:REMOVE) ([^\n\r]*)")
MISSING_COLON_REGEX = re.compile(r"\s*(?:ACTIE|TASK|ACTIES|TASKS)+[^:]*$")


def find_minute_by_id(minute_id):
    return pimpy_repository.find_minute_by_id(minute_id)


def find_task_by_id(task_id):
    return pimpy_repository.find_task_by_id(task_id)


def get_all_minutes_for_user(user):
    return pimpy_repository.get_all_minutes_for_user(user)


def check_date_range(date_range):
    if date_range:
        if len(date_range) != 2:
            raise ValidationException("Date range should be of length 2")
        if not all(map(lambda x: type(x) == datetime.datetime,
                       date_range)):
            raise ValidationException("Date range should consist of datetime")
        if date_range[0] > date_range[1]:
            raise ValidationException(
                "First date should be smaller then second")


def get_all_minutes_for_group(group_id, date_range=None):
    check_date_range(date_range)
    group = group_service.get_group_by_id(group_id)
    return pimpy_repository.get_all_minutes_for_group(group, date_range)


def get_all_tasks_for_user(user, date_range=None):
    check_date_range(date_range)
    return pimpy_repository.get_all_tasks_for_user(user, date_range)


def get_all_tasks_for_group(group_id, date_range=None, user=None):
    check_date_range(date_range)
    group = group_service.get_group_by_id(group_id)
    return pimpy_repository.get_all_tasks_for_group(group, date_range, user)


def get_all_tasks_for_users_in_groups_of_user(user, date_range=None):
    check_date_range(date_range)
    groups = group_service.get_groups_for_user(user)
    return pimpy_repository.get_all_tasks_for_users_in_groups(groups)


def set_task_status(user, task, status):
    if not user.member_of_group(task.group_id) and user not in task.users:
        raise ValidationException('User not member of group of task')

    valid = (PimpyTaskStatus.NOT_STARTED.value <= status <=
             PimpyTaskStatus.MAX.value)
    if not valid:
        raise ValidationException('Status not valid')

    return pimpy_repository.update_status(task, status)


def get_task_status_choices():
    return list(map(lambda index, status: (index, status),
                    range(0, len(Task.status_meanings)),
                    Task.status_meanings))


def add_task_by_user_string(title, content, group_id, users_text, line,
                            minute, status):
    group = group_service.get_group_by_id(group_id)
    user_list = get_list_of_users_from_string(group_id, users_text)

    _add_task(title=title, content=content, group=group,
              user_list=user_list, minute=minute, line=line,
              status=status)


def _add_task(title, content, group, user_list, line, minute, status):
    # Only check for tasks added not using minute.
    if not minute:
        task = task_repository.find_task_by_name_content_group(
            title, content, group)

        if task:
            raise ValidationException("This task already exists")
    pimpy_repository.add_task(title=title, content=content, group=group,
                              users=user_list, minute=minute, line=line,
                              status=status)


def add_minute(content, date, group):
    # Parse the minute
    task_list, done_list, remove_list = _parse_minute_into_tasks(
        content, group)

    minute = pimpy_repository.add_minute(content=content, date=date,
                                         group=group)
    # Add new tasks
    for line, task, users in task_list:
        _add_task(task, '', group, users, line, minute, 0)

    # Mark existing tasks as done.
    for line, task in done_list:
        task = pimpy_repository.find_task_by_id(task)
        pimpy_repository.update_status(task, 4)

    # Mark existing tasks as removed.
    for line, task in remove_list:
        task = pimpy_repository.find_task_by_id(task)
        pimpy_repository.update_status(task, 5)
    return minute


def edit_task_property(user, task_id, content=None, title=None,
                       users_property=None):
    task = find_task_by_id(task_id)

    if not user.member_of_group(task.group_id):
        raise ValidationException('User not member of group of task')
    if content is not None:
        pimpy_repository.edit_task_content(task, content)

    if title is not None:
        pimpy_repository.edit_task_title(task, title)

    if users_property is not None:
        users = get_list_of_users_from_string(task.group_id, users_property)
        pimpy_repository.edit_task_users(task, users)


def get_list_of_users_from_string(group_id, comma_sep_users):
    """
    Get the list of users from a comma separated string of usernames.

    Parses a string which is a list of comma separated user names
    to a list of users, searching only within the group given

    :arg group_id is the group's id
    :arg comma_sep_users is a string with comma separated users.
    """
    group = group_service.get_group_by_id(group_id)

    if comma_sep_users is None:
        raise ValidationException('No comma separated list of users found.')

    comma_sep_users = comma_sep_users.strip()

    if not comma_sep_users:
        return group.users.all()

    comma_sep_users = filter(None, map(lambda x: x.lower().strip(),
                                       comma_sep_users.split(',')))

    users_found = []

    users = group.users.all()

    for comma_sep_user in comma_sep_users:
        maximum = 0
        match = None

        for user in users:
            rate_first = fuzz.ratio(user.first_name.lower(), comma_sep_user)
            rate_last = fuzz.ratio(user.last_name.lower(), comma_sep_user)
            rate_full = fuzz.ratio(user.name.lower(), comma_sep_user)

            new_max = max(rate_first, rate_last, rate_full)
            if new_max > maximum:
                maximum = new_max
                match = user

        if not match:
            raise ValidationException(
                "Could not find a user for %s" % comma_sep_user)

        users_found.append(match)

    return users_found


def _parse_minute_into_tasks(content, group):
    """
    Parse the specified minutes for tasks and return task, done and remove.

    Syntax within the content:
    ACTIE <name_1>, <name_2>, name_n>: <title of task>
    This creates a single task for one or multiple users

    ACTIES <name_1>, <name_2>, name_n>: <title of task>
    This creates one or multiple tasks for one or multiple users

    DONE <task1>, <task2, <taskn>
    This sets the given tasks on 'done'
    """
    invalid_lines = []

    task_list = []
    done_list = []
    remove_list = []

    for i, line in enumerate(content.splitlines()):
        try:
            if MISSING_COLON_REGEX.search(line):
                invalid_lines.append((i, line))
                continue

            # Single task for multiple users.
            for names, task in TASK_REGEX.findall(line):
                users = get_list_of_users_from_string(group.id, names)
                task_list.append((i, task, users))

            # Single task for individual users.
            for names, task in TASKS_REGEX.findall(line):
                users = get_list_of_users_from_string(group.id, names)
                for user in users:
                    task_list.append((i, task, [user]))

            # Mark a comma separated list as done.
            for task_id_list in DONE_REGEX.findall(line):
                for b32_task_id in task_id_list.strip().split(","):
                    done_list.append((i, b32.decode(b32_task_id.strip())))

            # Mark a comma separated list as removed.
            for task_id_list in REMOVE_REGEX.findall(line):
                for b32_task_id in task_id_list.strip().split(","):
                    remove_list.append((i, b32.decode(b32_task_id.strip())))

        # Catch invalid user and incorrect b32 task_id.
        except (ValidationException, ValueError):
            invalid_lines.append((i, line))

    if len(invalid_lines):
        raise InvalidMinuteException(invalid_lines)

    return task_list, done_list, remove_list
