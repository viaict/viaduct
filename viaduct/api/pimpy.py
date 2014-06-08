from viaduct import db, application
from flask import render_template, Markup, redirect, url_for, abort,\
    flash
from flask.ext.login import current_user
from unidecode import unidecode
import datetime
import re
import difflib

from viaduct.api.group import GroupPermissionAPI
from viaduct.api.user import UserAPI
from viaduct.models import Group, User
from viaduct.models import Minute, Task
from viaduct.models.pimpy import TaskUserRel

DATE_FORMAT = application.config['DATE_FORMAT']


class PimpyAPI:
    @staticmethod
    def commit_minute_to_db(content, date, group_id):
        """
        Enter minute into the database.
        Return succes (boolean, message (string). Message is the new minute.id
        if succes is true, otherwise it contains an error message.
        """
        if not GroupPermissionAPI.can_write('pimpy'):
            abort(403)

        try:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
        except:
            if date != "":
                return False, "Could not parse the date"
            date = None

        minute = Minute(content, group_id, date)
        db.session.add(minute)
        db.session.commit()

        return True, minute.id

    @staticmethod
    def commit_task_to_db(name, content, deadline, group_id, filled_in_users,
                          line, minute_id, status):
        """
        Enter task into the database.
        Return succes (boolean), message (string). Message is the new task.id
        if succes is true, otherwise it contains an error message.
        """
        if not GroupPermissionAPI.can_write('pimpy'):
            abort(403)

        if group_id == 'all':
            return False, "Group can not be 'all'"
        group = Group.query.filter(Group.id == group_id).first()
        if group is None:
            return False, "Could not distinguish group."

        users, message = PimpyAPI.get_list_of_users_from_string(
            group_id, filled_in_users)
        if not users:
            return False, message

        try:
            deadline = datetime.datetime.strptime(deadline, DATE_FORMAT)
        except:
            if deadline != "":
                return False, "Could not parse the deadline"
            deadline = None

        if minute_id <= 0:
            minute_id = 1

        task = Task(name, content, deadline, group_id,
                    users, minute_id, line, status)
        db.session.add(task)
        db.session.commit()
        return True, task.id

    @staticmethod
    def edit_task(task_id, name, content, deadline, group_id,
                  filled_in_users, line):
        """
        Returns succes (boolean), message (string). Message is irrelevant if
        succes is true, otherwise it contains what exactly went wrong.

        In case of succes the task is edited in the database.
        """
        if not GroupPermissionAPI.can_write('pimpy'):
            abort(403)

        if task_id == -1:
            return False, "no task_id given"

        task = Task.query.filter(Task.id == task_id).first()

        users, message = PimpyAPI.get_list_of_users_from_string(
            group_id, filled_in_users)
        if not users:
            return False, message

        if name:
            task.title = name
        if content:
            task.content = content
        if deadline:
            try:
                deadline = datetime.datetime.strptime(deadline, DATE_FORMAT)
            except:
                if deadline != "":
                    return False, "Could not parse the deadline"
                deadline = None
            task.deadline = deadline
        if group_id:
            task.group_id = group_id
        if line:
            task.line = line
        if users:
            task.users = users
    #   if status:
    #       task.status = status

        db.session.commit()
        return True, "task edited"

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

        regex = re.compile("\s*(?:ACTIE|TODO) ([^\n\r]*)")
        for i, line in enumerate(content.splitlines()):
            matches = regex.findall(line)
            for action in matches:
                try:
                    listed_users, title = action.split(":", 1)
                except:
                    print("could not split the line on ':'.\nSkipping hit.")
                    flash("could not parse: " + action)
                    continue

                users, message = PimpyAPI.get_list_of_users_from_string(
                    group_id, listed_users)
                if not users:
                    print(message)
                    continue
                try:
                    task = Task(title, "", None, group_id, users,
                                minute_id, i, 0)
                except:
                    print("wasnt given the right input to create a task")
                    continue
                tasks_found.append(task)

        regex = re.compile("\s*(?:ACTIES|TODOS) ([^\n\r]*)")
        for i, line in enumerate(content.splitlines()):
            matches = regex.findall(line)
            for action in matches:
                try:
                    listed_users, title = action.split(":", 1)
                except:
                    print("could not split the line on ':'.\nSkipping hit.")
                    flash("could not parse: " + action)
                    continue

                users, message = PimpyAPI.get_list_of_users_from_string(
                    group_id, listed_users)
                if not users:
                    print(message)
                    continue
                for user in users:
                    try:
                        task = Task(title, "", None, group_id, [user],
                                    minute_id, i, 0)
                    except:
                        print("wasnt given the right input to create a task")
                        continue
                    tasks_found.append(task)

        regex = re.compile("\s*(?:DONE) ([^\n\r]*)")
        matches = regex.findall(content)
        for match in matches:
            done_ids = match.split(",")
            for done_id in done_ids:
                try:
                    done_task = Task.query.filter(Task.id == done_id).first()
                except:
                    print("could not find the given task")
                    flash("could not find DONE " + done_id)
                    continue
                dones_found.append(done_task)

        regex = re.compile("\s*(?:REMOVE) ([^\n\r]*)")
        matches = regex.findall(content)
        for match in matches:
            remove_ids = match.split(",")
            for remove_id in remove_ids:
                try:
                    remove_task = Task.query.filter(Task.id == remove_id).first()
                except:
                    print("could not find the given task")
                    flash("could not find REMOVE " + remove_id)
                    continue
                removes_found.append(remove_task)

        return tasks_found, dones_found, removes_found

    @staticmethod
    def get_list_of_users_from_string(group_id, comma_sep):
        """
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
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)

        group = Group.query.filter(Group.id == group_id).first()
        if group is None:
            return False, "Could not distinguish group."

        if comma_sep is None:
            return False, "Did not receive any comma separated users"

        comma_sep = map(lambda x: x.lower().strip(), comma_sep.split(','))

        found_users = []

        users = group.users.all()

        user_names = map(lambda x: "%s %s" % (x.first_name.lower().strip(),
                                              x.last_name.lower().strip()),
                         users)
        user_names = [unidecode(x) for x in user_names]

        for comma_sep_user in comma_sep:

            temp_found_users = []
            match = difflib.get_close_matches(comma_sep_user, user_names, n=1, cutoff=0.5)
            for i in range(len(users)):

                # could use a filter here, but meh
                if user_names[i] == match:
                    temp_found_users.append(users[i])

            if len(temp_found_users) == 0:
                # We want to add an action to all users if none has been found
                temp_found_users = users

            # We actually want to be able to add tasks to more than 1 user
            # if len(temp_found_users) > 1:
            #     return False, "could not disambiguate %s" % comma_sep_user

            found_users.extend(temp_found_users)
        return found_users, ""

    @staticmethod
    def get_navigation_menu(group_id, personal, type):
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)
        if not current_user:
            flash('Current_user not found')
            return redirect(url_for('pimpy.view_minutes'))

        groups = current_user.groups.filter(Group.name != 'all').order_by(Group.name.asc()).all()

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

        if not group_id:
            group_id = 'all'
        if group_id != 'all':
            group_id = int(group_id)

        return Markup(render_template('pimpy/api/side_menu.htm', groups=groups,
                                      group_id=group_id, personal=personal,
                                      type=type, endpoints=endpoints))

    @staticmethod
    def get_all_tasks(group_id):
        """
        Shows all tasks ever made.
        Can specify specific group.
        No internal permission system made yet.
        Do not make routes to this module yet.
        """
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)
        if not current_user:
            flash('Current_user not found')
            return redirect(url_for('pimpy.view_tasks'))

        status_meanings = Task.get_status_meanings()

        list_items = {}
        if group_id == 'all':
            for group in UserAPI.get_groups_for_current_user():
                list_users = {}
                list_users['Iedereen'] = group.tasks
                list_items[group.name] = list_users
        else:
            list_users = {}
            tasks = Task.query.filter(Task.group_id == group_id).all()
            group = Group.query.filter(Group.id == group_id).first()
            if not group:
                abort(404)
            if not group in UserAPI.get_groups_for_current_user():
                abort(403)
            list_users['Iedereen'] = tasks
            list_items[group.name] = list_users

        return Markup(render_template('pimpy/api/tasks.htm',
                                      list_items=list_items, type='tasks',
                                      group_id=group_id, personal=False,
                                      status_meanings=status_meanings))

    @staticmethod
    def get_tasks(group_id, personal):
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)
        if not current_user:
            flash('Current_user not found')
            return redirect(url_for('pimpy.view_tasks'))

        status_meanings = Task.get_status_meanings()

        tasks_rel = TaskUserRel.query.join(Task).join(User)

        groups = UserAPI.get_groups_for_current_user()
        groups = map(lambda x: x.id, groups)

        if group_id == 'all':
            tasks_rel = tasks_rel.filter(Task.group_id.in_(groups))

        else:
            group_id = int(group_id)
            if group_id not in groups:
                abort(403)

            tasks_rel = tasks_rel.filter(Task.group_id == group_id)

        if personal:
            tasks_rel = tasks_rel.filter(User.id == current_user.id)

        tasks_rel = tasks_rel.filter(~Task.status.in_((4, 5))).join(Group)
        tasks_rel = tasks_rel.order_by(Group.name.asc(), User.first_name.asc(),
                                       User.last_name.asc(), Task.id.asc())

        return Markup(render_template('pimpy/api/tasks.htm',
                                      personal=personal,
                                      group_id=group_id,
                                      tasks_rel=tasks_rel,
                                      type='tasks',
                                      status_meanings=status_meanings))

    @staticmethod
    def get_minutes(group_id):
        """
        Load all minutes in the given group
        """
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)
        if not current_user:
            flash('Current_user not found')
            return redirect(url_for('pimpy.view_minutes'))

        list_items = {}

        if group_id != 'all':
            query = Minute.query.filter(Minute.group_id == group_id).\
                order_by(Minute.minute_date.desc())
            list_items[Group.query.filter(Group.id == group_id).first().name]\
                = query.all()
        # this should be done with a sql in statement, or something, but meh
        else:
            for group in current_user.groups:
                query = Minute.query.filter(Minute.group_id == group.id)
                query = query.order_by(Minute.minute_date.desc())
                list_items[group.name] = query.all()

        return Markup(render_template('pimpy/api/minutes.htm',
                                      list_items=list_items, type='minutes',
                                      group_id=group_id, line_number=-1))

    @staticmethod
    def get_minute(group_id, minute_id, line_number):
        """
        Load (and thus view) specifically one minute
        """
        if not GroupPermissionAPI.can_read('pimpy'):
            abort(403)
        if not current_user:
            flash('Current_user not found')
            return redirect(url_for('pimpy.view_minutes'))

        list_items = {}
        query = Minute.query.filter(Minute.id == minute_id)
        group = Group.query.filter(Group.id == group_id).first()
        list_items[group.name] = query.all()
        tag = "%dln%d" % (list_items[group.name][0].id, int(line_number))

        #return Markup(render_template('pimpy/api/minutes.htm',
        #                              list_items=list_items, type='minutes',
        #                              group_id=group_id, line_number=line_number))
        return render_template('pimpy/api/minutes.htm',
                                      list_items=list_items, type='minutes',
                                      group_id=group_id,
                                      line_number=line_number,
                                      tag=tag)

    @staticmethod
    def update_content(task_id, content):
        """
        Update the content of the task with the given id
        """
        task = Task.query.filter(Task.id == task_id).first()
        task.content = content
        db.session.commit()
        return True, "The task is edited sucessfully"

    @staticmethod
    def update_title(task_id, title):
        """
        Update the title of the task with the given id
        """
        task = Task.query.filter(Task.id == task_id).first()
        task.title = title
        db.session.commit()
        return True, "The task is edited sucessfully"

    @staticmethod
    def update_users(task_id, comma_sep_users):
        """
        Update the users of the task with the given id
        """
        task = Task.query.filter(Task.id == task_id).first()
        users, message = PimpyAPI.get_list_of_users_from_string(
            task.group_id, comma_sep_users)
        if not users:
            return False, message
        task.users = users
        db.session.commit()
        return True, "The task is edited sucessfully"

    @staticmethod
    def update_date(task_id, date):
        """
        Update the date of the task with the given id
        """
        try:
            date = datetime.datetime.strptime(date, DATE_FORMAT)
        except:
            if date != "":
                return False, "Could not parse the date"
            date = None

        task = Task.query.filter(Task.id == task_id).first()
        task.deadline = date
        db.session.commit()
        return True, "The task is edited sucessfully"
