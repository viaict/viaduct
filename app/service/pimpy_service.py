from fuzzywuzzy import fuzz

from app.exceptions import ValidationException
from app.models.group import Group
from app.models.pimpy import Task
from app.repository import pimpy_repository, group_repository, task_repository

"""
What is pimpy?

Pimpy; Precise Inscriptions of Minutes with Python.
The minute system of the study association via.

Pimpy is used for handling the minutes and tasks of different groups.
By using different keywords in the minutes tasks are extracted and automatically
created.

The Minute(s) are the notes of a meeting where the written text is in.
With actions in these notes new Task(s) are created. These are bound to users, and have
a status.


"""


def find_minute_by_id(minute_id):
    return pimpy_repository.find_minute_by_id(minute_id)


def find_task_by_id(task_id):
    return pimpy_repository.find_task_by_id(task_id)


def get_all_minutes_for_user(user):
    return pimpy_repository.get_all_minutes_for_user(user)


def get_all_minutes_for_group(group_id, date_range=None):
    # TODO: get group here and use that to query the repo
    return pimpy_repository.get_all_minutes_for_group(group_id, date_range)


def get_all_tasks_for_groups(group_ids, date_range=None, user=None):
    # TODO: get group here and use that to query the repo
    return pimpy_repository.get_all_tasks_for_groups(
        group_ids, date_range, user)


def update_status(user, task, status):
    if not user.member_of_group(task.group_id):
        raise ValidationException('User not member of group of task')

    valid = 0 <= status <= len(Task.status_meanings)
    if not valid:
        raise ValidationException('Status not valid')

    return pimpy_repository.update_status(task, status)


def add_task(name, content, group_id, users_text, line, minute_id, status):
    # TODO: get group here and use that to query the repo
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ValidationException(
            'Er is niet een groep die voldoet opgegeven.')

    users = get_list_of_users_from_string(group_id, users_text)

    # TODO: remove
    if minute_id <= 0:
        minute_id = 1

    task = task_repository.find_task_by_name_content_group(
        name, content, group)

    if task:
        raise ValidationException('Deze taak bestaat al in de database')
    else:
        task = Task(name, content, group_id, users, minute_id, line, status)

    pimpy_repository.add_task(task)


def edit_task_property(user, task_id, property, value):
    task = find_task_by_id(task_id)

    if not user.member_of_group(task.group_id):
        raise ValidationException('User not member of group of task')

    if property == 'content':
        pimpy_repository.edit_task_content(task, value)
    elif property == 'title':
        pimpy_repository.edit_task_title(task, value)
    elif property == 'users':
        users = get_list_of_users_from_string(task.group_id, value)
        pimpy_repository.edit_task_users(task, users)
    else:
        raise ValidationException('Invalid property to edit')


def get_list_of_users_from_string(group_id, comma_sep):
    """
    Get the list of users from a comma seperated string of usernames.

    Parses a string which is a list of comma separated user names
    to a list of users, searching only within the group given

    usage:
    get_list_of_users_from_string(group_id, comma_sep)
    where group_id is the group's id
    and comma_sep is a string with comma separated users.
    """

    group = Group.query.filter(Group.id == group_id).first()
    if group is None:
        raise ValidationException('Kan groep niet vinden.')

    if comma_sep is None:
        raise ValidationException('Geen komma gescheiden lijst met gebruikers '
                                  'gevonden.')

    comma_sep = comma_sep.strip()

    if not comma_sep:
        return group.users.all(), ''

    comma_sep = filter(None, map(lambda x: x.lower().strip(),
                                 comma_sep.split(',')))

    users_found = []

    users = group.users.all()

    user_names = []

    for user in users:
        x = {"id": user.id,
             "first_name": user.first_name.lower().strip(),
             "last_name": user.last_name.lower().strip()}
        user_names.append(x)

    for comma_sep_user in comma_sep:
        maximum = 0
        match = -1

        for user_name in user_names:
            rate = fuzz.ratio(user_name['first_name'], comma_sep_user)
            rate_last = fuzz.ratio(user_name['last_name'], comma_sep_user)

            full_name = user_name['first_name'] + ' ' + user_name['last_name']
            rate_full = fuzz.ratio(full_name, comma_sep_user)

            if rate > maximum or rate_last > maximum or rate_full > maximum:
                maximum = max(rate, rate_last)
                match = user_name['id']

        found = False

        if match < 0:
            raise ValidationException(
                'Kon geen gebruiker vinden voor: %s' % (comma_sep_user))

        for user in users:
            if user.id == match:
                users_found.append(user)
                found = True
                break

        if not found:
            raise ValidationException(
                'Kon geen gebruiker vinden voor: %s' % (comma_sep_user))

    return users_found
