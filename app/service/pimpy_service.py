from fuzzywuzzy import fuzz

from app.exceptions import ValidationException, ResourceNotFoundException
from app.models.pimpy import Task
from app.repository import pimpy_repository, group_repository, task_repository
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


def find_minute_by_id(minute_id):
    return pimpy_repository.find_minute_by_id(minute_id)


def find_task_by_id(task_id):
    return pimpy_repository.find_task_by_id(task_id)


def get_all_minutes_for_user(user):
    return pimpy_repository.get_all_minutes_for_user(user)


def get_all_minutes_for_group(group_id, date_range=None):
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundException("group", group_id)

    return pimpy_repository.get_all_minutes_for_group(group, date_range)


def get_all_tasks_for_user(user, date_range=None):
    return pimpy_repository.get_all_tasks_for_user(user, date_range)


def get_all_tasks_for_group(group_id, date_range=None, user=None):
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundException("group", group_id)

    return pimpy_repository.get_all_tasks_for_group(group, date_range, user)


def set_task_status(user, task, status):
    if not user.member_of_group(task.group_id) and user not in task.users:
        raise ValidationException('User not member of group of task')

    valid = 0 <= status <= Task.STATUS_MAX
    if not valid:
        raise ValidationException('Status not valid')

    return pimpy_repository.update_status(task, status)


def add_task(title, content, group_id, users_text, line, minute_id, status):
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundException("group", group_id)

    users = get_list_of_users_from_string(group_id, users_text)

    task = task_repository.find_task_by_name_content_group(
        title, content, group)

    if task:
        raise ValidationException("This task already exists")
    else:
        task = Task(title=title, content=content, group_id=group_id,
                    users=users, minute_id=minute_id, line=line,
                    status=status)

    pimpy_repository.add_task(task)


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
        print(users)
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
        return group.users.all(), ''

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


def get_task_status_choices():
    return list(map(lambda index, status: (index, status),
                    range(0, len(Task.status_meanings)),
                    Task.status_meanings))
