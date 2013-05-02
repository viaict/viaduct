from flask import render_template, request, Markup, redirect, url_for, abort
from flask.ext.login import current_user

from models import Task, Minute

from viaduct.blueprints.group.models import Group
from viaduct.blueprints.user.models import User

from viaduct import db


import datetime


class PimpyAPI:

	@staticmethod
	def commit_task_to_db(name, content, deadline, group_id,
		filled_in_users, line, minute_id, status):
		"""
		Returns succes (boolean), message (string). Message is irrelevant if
		success is true, otherwise it contains what exactly went wrong.

		In case of succes the task is entered into the database
		"""

		if group_id == 'all':
			return False, "Group can not be 'all'"
		group = Group.query.filter(Group.id==group_id).first()
		if group == None:
			return False, "Could not distinguish group."

		users, message = PimpyAPI.get_list_of_users_from_string(group,
			filled_in_users)
		if not users:
			return False, message

		deadline = datetime.datetime.strptime(deadline, "%m/%d/%Y")

		task = Task(name, content, deadline, group_id,
				users, line, minute_id, status)
		db.session.add(task)
		db.session.commit()
		return True, "jaja"

	@staticmethod
	def get_list_of_users_from_string(group, comma_sep):
		"""
		Parses a string which is a list of comma separated user names
		to a list of users, searching only within the group given

		Returns users, message. Users is false if there is something wrong,
		in which case the message is stated in message, otherwise message
		equals "" and users is the list of matched users

		Should, in the future, return specific error messages when the
		matching fails.
		"""

		if comma_sep == None:
			return False, "Did not receive any comma separated users"

		comma_sep = map(lambda x: x.lower().strip(), comma_sep.split(','))

		found_users = []

		users = group.users.all()

		user_names = map(lambda x: "%s %s" % (x.first_name.lower().strip(), x.last_name.lower().strip()), users)

		for comma_sep_user in comma_sep:
			print "comma sep user: ", comma_sep_user

			for i in range(len(users)):
				print "user name:", user_names[i]

				# could use a filter here, but meh
				if user_names[i].startswith(comma_sep_user):
					print "Found %s matchin' with %s" % (comma_sep_user,
						user_names[i])
					found_users.append(users[i])

			if len(found_users) == 0:
				return False, "Could not match %s to a user in the group" % comma_sep_user
			if len(found_users) > 1:
				return False, "could not disambiguate %s" % comma_sep_user

		return found_users, ""

	@staticmethod
	def check_user_is_logged_in():
		print "_%s_ _%s_ _%s_ _%s_" % (current_user.first_name, current_user.last_name, current_user.email, current_user.is_authenticated())
		if not current_user.is_authenticated():
			abort(401)
		return ""

	@staticmethod
	def get_navigation_menu(group_id, personal, type):
		groups = current_user.groups.all()

		endpoint = 'pimpy.view_' + type
		endpoints = {'view_chosentype' : endpoint,
					'view_chosentype_personal' : endpoint + '_personal',
					'view_chosentype_chosenpersonal' : endpoint + (('_personal' if personal else '') if type != 'minutes' else ''),
					'view_tasks' : 'pimpy.view_tasks',
					'view_tasks_personal' : 'pimpy.view_tasks_personal',
					'view_tasks_chosenpersonal' : 'pimpy.view_tasks',
					'view_minutes' : 'pimpy.view_minutes'}
		if personal:
			endpoints['view_tasks_chosenpersonal'] += '_personal'

		if group_id != 'all':
			group_id = int(group_id)

		return Markup(render_template('pimpy/api/side_menu.htm',
			groups=groups, group_id=group_id, personal=personal,
			type=type, endpoints=endpoints))

	@staticmethod
	def get_tasks(group_id, personal):
		# TODO: only return tasks with status != completed

		list_items = []


		if personal:
			query = current_user.tasks
			if group_id == 'all':
				list_items.extend(query.all())
			else:
				query = query.filter(Task.group_id==group_id)
				list_items.extend(query.all())
		else:
			if group_id == 'all':
				groups = current_user.groups
				for group in groups:
					list_items.extend(group.tasks.all())
			else:
				query = current_user.tasks
				query = query.filter(Task.group_id==group_id)
				list_items.extend(query.all())

		return Markup(render_template('pimpy/api/tasks.htm',
			list_items=list_items, type='tasks', group_id=group_id,
			personal=personal))

	@staticmethod
	def get_minutes(group_id):
		list_items = []

		query = Minute.query
		if group_id != 'all':
			query = query.filter(Minute.group_id==group_id)
		list_items.extend(query.all())

		return Markup(render_template('pimpy/api/minutes.htm',
			list_items=list_items, type='minutes', group_id=group_id))

	@staticmethod
	def get_minute(group_id, minute_id):
		"""
		Loads (and thus views) specifically one minute
		"""
		query = Minute.query
		query = query.filter(Minute.id==minute_id)
		list_items = query.all()

		return Markup(render_template('pimpy/api/minutes.htm',
			list_items=list_items, type='minutes', group_id=group_id))

