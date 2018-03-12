import datetime
import re

import baas32 as b32
from flask import render_template, Markup, redirect, url_for, \
    flash
from flask_babel import _
from flask_login import current_user
from fuzzywuzzy import fuzz
from unidecode import unidecode

from app import db, app
from app.models.group import Group
from app.models.pimpy import Minute, Task

# from app.utils import copernica

DATE_FORMAT = app.config['DATE_FORMAT']


class PimpyAPI:
    @staticmethod
    def commit_minute_to_db(content, date, group_id):
        """
        Enter minute into the database.

        Return succes (boolean, message (string). Message is the new minute.id
        if succes is true, otherwise it contains an error message.
        """
        try:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
        except Exception:
            if date != "":
                return False, "De datum kon niet worden verwerkt."
            date = None

        minute = Minute(content=content, group_id=group_id, minute_date=date)
        db.session.add(minute)
        db.session.commit()

        return True, minute.id

    @staticmethod
    def parse_minute(content, group_id, minute_id):
        """
        Parse the specified minutes for tasks and return them in a list.

        Same for DONE tasks and REMOVED tasks

        syntax within the content:
        ACTIE <name_1>, <name_2>, name_n>: <title of task>
        or
        TODO <name_1>, <name_2>, name_n>: <title of task>
        this creates a single task for one or multiple users

        ACTIES <name_1>, <name_2>, name_n>: <title of task>
        or
        TODOS <name_1>, <name_2>, name_n>: <title of task>
        this creates one or multiple tasks for one or multiple users

        DONE <task1>, <task2, <taskn>
        this sets the given tasks on 'done'

        usage:
        tasks, dones, removes = parse_minute(content, group_id, minute_id)
        where content is a string with the entire minute
        """

        tasks_found = []
        dones_found = []
        removes_found = []

        regex = re.compile(r"\s*(?:ACTIE|TODO)([\s:]\s*[^\n\r]*)")
        for i, line in enumerate(content.splitlines()):
            matches = regex.findall(line)

            for action in matches:
                try:
                    listed_users, title = action.split(":", 1)
                except Exception:
                    print("could not split the line on ':'.\nSkipping hit.")
                    flash("Kon niet verwerken: " + str(action), 'danger')
                    continue

                users, message = PimpyAPI.get_list_of_users_from_string(
                    group_id, listed_users)
                if not users:
                    print(message)
                    continue

                try:
                    task = Task(title=title, content="", group_id=group_id,
                                users=users, minute_id=minute_id, line=i,
                                status=0)
                except Exception:
                    print("wasnt given the right input to create a task")
                    continue
                tasks_found.append(task)

        regex = re.compile("\s*(?:ACTIES|TODOS)([^\n\r]*:\s*[^\n\r]*)")
        for i, line in enumerate(content.splitlines()):
            matches = regex.findall(line)

            for action in matches:
                try:
                    listed_users, title = action.split(":", 1)
                except Exception:
                    print("could not split the line on ':'.\nSkipping hit.")
                    flash("Kon niet verwerken: " + action, 'danger')
                    continue

                users, message = PimpyAPI.get_list_of_users_from_string(
                    group_id, listed_users)
                if not users:
                    print(message)
                    continue

                for user in users:
                    try:
                        task = Task(title=title, content="", group_id=group_id,
                                    users=[user], minute_id=minute_id, line=i,
                                    status=0)
                    except Exception:
                        print("wasnt given the right input to create a task")
                        continue
                    tasks_found.append(task)

        regex = re.compile("\s*(?:DONE) ([^\n\r]*)")
        matches = regex.findall(content)
        for match in matches:
            done_ids = filter(None, match.split(","))

            for b32_id in done_ids:
                b32_id_strip = b32_id.strip()
                if b32_id_strip == '':
                    continue
                try:
                    done_id = b32.decode(b32_id_strip)
                except ValueError:
                    flash(_("Invalid DONE task id: ") + b32_id_strip,
                          'danger')
                    continue

                done_task = Task.query.filter(Task.id == done_id).first()

                if done_task is None:
                    flash(_("Could not find DONE task: ") + b32_id_strip,
                          "danger")
                    continue

                dones_found.append(done_task)

        regex = re.compile("\s*(?:REMOVE) ([^\n\r]*)")
        matches = regex.findall(content)
        for match in matches:
            remove_ids = filter(None, match.split(","))

            for b32_id in remove_ids:
                b32_id_strip = b32_id.strip()
                if b32_id_strip == '':
                    continue

                try:
                    remove_id = b32.decode(b32_id_strip)
                except ValueError:
                    flash(_("Invalid REMOVE task id: ") + b32_id,
                          'danger')
                    continue

                remove_task = Task.query\
                    .filter(Task.id == remove_id).first()
                if remove_task is None:
                    flash(_("Could not find REMOVE task: ") + b32_id_strip,
                          "danger")
                    continue

                removes_found.append(remove_task)

        return tasks_found, dones_found, removes_found

    @staticmethod
    def get_list_of_users_from_string(group_id, comma_sep):
        """
        Get the list of users from a comma seperated string of usernames.

        Parses a string which is a list of comma separated user names
        to a list of users, searching only within the group given
        Returns users, message. Users is false if there is something wrong,
        in which case the message is stated in message, otherwise message
        equals "" and users is the list of matched users

        usage:
        get_list_of_users_from_string(group_id, comma_sep)
        where group_id is the group's id
        and comma_sep is a string with comma seperated users.
        """

        group = Group.query.filter(Group.id == group_id).first()
        if group is None:
            return False, "Kan groep niet vinden."

        if comma_sep is None:
            return False,
        "Geen komma gescheiden lijst met gebruikers gevonden."

        comma_sep = comma_sep.strip()

        if not comma_sep:
            return group.users.all(), ''

        comma_sep = filter(None, map(lambda x: x.lower().strip(),
                                     comma_sep.split(',')))

        found_users = []

        users = group.users.all()

        user_names = []

        for user in users:
            x = {"id": user.id,
                 "first_name": unidecode(user.first_name.lower().strip()),
                 "last_name": unidecode(user.last_name.lower().strip())}
            user_names.append(x)

        for comma_sep_user in comma_sep:
            maximum = 0
            match = -1

            for user_name in user_names:
                rate = fuzz.ratio(user_name['first_name'], comma_sep_user)
                rate_last = fuzz.ratio(user_name['last_name'], comma_sep_user)

                full_name = user_name['first_name'] + ' ' \
                    + user_name['last_name']
                rate_full = fuzz.ratio(full_name, comma_sep_user)

                if rate > maximum or rate_last > maximum or \
                        rate_full > maximum:
                    maximum = max(rate, rate_last)
                    match = user_name['id']

            found = False

            if match < 0:
                return False, \
                    'Kon geen gebruiker vinden voor: %s' % (comma_sep_user)

            for user in users:
                if user.id == match:
                    found_users.append(user)
                    found = True
                    break

            if not found:
                return False, \
                    'Kon geen gebruiker vinden voor %s' % (comma_sep_user)

        return found_users, ""

    @staticmethod
    def get_navigation_menu(group_id, personal, type):
        if current_user.is_anonymous:
            flash('Huidige gebruiker niet gevonden!', 'danger')
            return redirect(url_for('pimpy.view_minutes'))

        if not type:
            type = 'minutes'
        endpoint = 'pimpy.view_' + type
        endpoints = {'view_chosentype': endpoint,
                     'view_chosentype_personal': endpoint + '_personal',
                     'view_chosentype_chosenpersonal': endpoint +
                     ('_personal' if personal and type != 'minutes' else ''),
                     'view_tasks': 'pimpy.view_tasks',
                     'view_tasks_personal': 'pimpy.view_tasks_personal',
                     'view_tasks_chosenpersonal': 'pimpy.view_tasks',
                     'view_minutes': 'pimpy.view_minutes'}
        if personal:
            endpoints['view_tasks_chosenpersonal'] += '_personal'

        return Markup(render_template('pimpy/api/side_menu.htm',
                                      groups=current_user.groups,
                                      group_id=group_id, personal=personal,
                                      type=type, endpoints=endpoints,
                                      title='PimPy'))

    @staticmethod
    def get_minutes_in_date_range(group_id, start_date, end_date):
        """Load all minutes in the given group."""

        if current_user.is_anonymous:
            flash('Huidige gebruiker niet gevonden', 'danger')
            return redirect(url_for('pimpy.view_minutes'))

        list_items = {}

        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        if group_id is None:
            for group in current_user.groups:
                query = Minute.query.filter(Minute.group_id == group.id)
                query = query.order_by(Minute.minute_date.desc())
                list_items[group.name] = query.all()
        else:
            query = Minute.query.filter(Minute.group_id == group_id).\
                filter(start_date <= Minute.minute_date,
                       Minute.minute_date <= end_date).\
                order_by(Minute.minute_date.desc())
            list_items[Group.query.filter(Group.id == group_id).first().name]\
                = query.all()

        return Markup(render_template('pimpy/api/minutes.htm',
                                      list_items=list_items, type='minutes',
                                      group_id=group_id, line_number=-1,
                                      title='PimPy'))

    @staticmethod
    def update_content(task_id, content):
        """Update the content of the task with the given id."""

        task = Task.query.get(task_id)
        if not task:
            return False, "Task does not exist"

        if not current_user.member_of_group(task.group_id):
            return False, "User not member of group of task"

        task.content = content
        db.session.commit()
        return True, "De taak is succesvol aangepast."

    @staticmethod
    def update_title(task_id, title):
        """Update the title of the task with the given id."""

        task = Task.query.get(task_id)
        if not task:
            return False, "Task does not exist"

        if not current_user.member_of_group(task.group_id):
            return False, "User not member of group of task"

        task.title = title
        db.session.commit()
        # for user in task.users:
        #     copernica_data = {
        #         "Actiepunt": task.title,
        #         "Status": task.get_status_string(),
        #     }
        #     copernica.update_subprofile(copernica.SUBPROFILE_TASK,
        #                                 user.id, task.base32_id(),
        #                                 copernica_data)
        return True, "De taak is succesvol aangepast."

    @staticmethod
    def update_users(task_id, comma_sep_users):
        """Update the users of the task with the given id."""

        task = Task.query.get(task_id)
        if not task:
            return False, "Task does not exist"

        if not current_user.member_of_group(task.group_id):
            return False, "User not member of group of task"

        # old_users = task.users
        users, message = PimpyAPI.get_list_of_users_from_string(
            task.group_id, comma_sep_users)
        if not users:
            return False, message

        # Sync to Copernica
        # for user in old_users:
        #     if user not in users:
        #         copernica_data = {
        #             "Actiepunt": task.title,
        #             "Status": task.get_status_string(),
        #         }
        #         copernica.update_subprofile(copernica.SUBPROFILE_TASK,
        #                                     user.id, task.base32_id(),
        #                                     copernica_data)
        # for user in users:
        #     if user not in old_users:
        #         copernica_data = {
        #             "viaductID": task.base32_id(),
        #             "Actiepunt": task.title,
        #             "Status": task.get_status_string(),
        #             "Groep": task.group.name,
        #         }
        #         copernica.add_subprofile(
        #             copernica.SUBPROFILE_TASK, user.id, copernica_data)

        task.users = users
        db.session.commit()
        return True, "De taak is succesvol aangepast."
