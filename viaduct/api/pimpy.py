from flask import render_template, request, Markup, redirect, url_for, abort, flash
from flask.ext.login import current_user

from viaduct.models import Group, User
from viaduct.models import Minute, Task

from sqlalchemy import desc

from viaduct import db, application

from viaduct.api.group import GroupPermissionAPI
from viaduct.api.user import UserAPI

import datetime
import re


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
	def commit_task_to_db(name, content, deadline, group_id,
		filled_in_users, line, minute_id, status):
		"""
		Enter task into the database.
		Return succes (boolean), message (string). Message is the new task.id
		if succes is true, otherwise it contains an error message.
		"""
		if not GroupPermissionAPI.can_write('pimpy'):
			abort(403)

		if group_id == 'all':
			return False, "Group can not be 'all'"
		group = Group.query.filter(Group.id==group_id).first()
		if group == None:
			return False, "Could not distinguish group."

		users, message = PimpyAPI.get_list_of_users_from_string(group_id,
			filled_in_users)
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

		if task_id==-1:
			return False, "no task_id given"

		task = Task.query.filter(Task.id==task_id).first()

		users, message = PimpyAPI.get_list_of_users_from_string(group_id,
			filled_in_users)
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
	#	if status:
	#		task.status = status

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

		usage:
		tasks, dones, removes = parse_minute(content, group_id, minute_id)
		where content is a string with the entire minute
		group id is the group's id
		minute id is the minute's id
		"""

		tasks_found = []
		dones_found = []
		removes_found = []

		regex = re.compile("\s*(?:ACTIE|TODO) ([^\n\r]*)")
		for i, line in enumerate(content.splitlines()):
			matches = regex.findall(line)
			for action in matches:
				try:
					listed_users, title = action.split(":")
				except:
					print "could not split the line on ':'.\nSkipping hit."
					flash("could not parse: " + action)
					continue

				users, message = PimpyAPI.get_list_of_users_from_string(group_id, listed_users)
				if not users:
					print message
					continue
				try:
					task = Task(title, "", None, group_id, users, minute_id,
						i, 0)
				except:
					print "wasnt given the right input to create a task"
					continue
				tasks_found.append(task)

		regex = re.compile("\s*(?:DONE) ([^\n\r]*)")
		matches = regex.findall(content)
		for done_id in matches:
			try:
				done_task = Task.query.filter(Task.id==done_id).first()
			except:
				print "could not find the given task"
				flash("could not find DONE " + done_id)
				continue
			if done_task:
				dones_found.append(done_task)
			else:
				print "Could not find task " + done_id
				flash("could not find DONE " + done_id)

		regex = re.compile("\s*(?:REMOVE) ([^\n\r]*)")
		matches = regex.findall(content)
		for remove_id in matches:
			try:
				remove_task = Task.query.filter(Task.id==remove_id).first()
			except:
				print "could not find the given task"
				flash("could not find REMOVE " + remove_id)
				continue
			if remove_task:
				removes_found.append(remove_task)
			else:
				print "Could not find REMOVE " + remove_id
				flash("could not find REMOVE " + remove_id)

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

		group = Group.query.filter(Group.id==group_id).first()
		if group == None:
			return False, "Could not distinguish group."

		if comma_sep == None:
			return False, "Did not receive any comma separated users"

		comma_sep = map(lambda x: x.lower().strip(), comma_sep.split(','))

		found_users = []

		users = group.users.all()

		user_names = map(lambda x: "%s %s" % (x.first_name.lower().strip(), x.last_name.lower().strip()), users)

		for comma_sep_user in comma_sep:

			temp_found_users = []
			for i in range(len(users)):

				# could use a filter here, but meh
				if user_names[i].startswith(comma_sep_user):
					temp_found_users.append(users[i])

			if len(temp_found_users) == 0:
				return False, "Could not match %s to a user in the group" % comma_sep_user
			if len(temp_found_users) > 1:
				return False, "could not disambiguate %s" % comma_sep_user
			found_users.extend(temp_found_users)
		return found_users, ""

	@staticmethod
	def get_navigation_menu(group_id, personal, type):
		if not GroupPermissionAPI.can_read('pimpy'):
			abort(403)
		if not current_user:
			flash('Current_user not found')
			return redirect(url_for('pimpy.view_minutes'))

		groups = current_user.groups.all()

		if not type:
			type='minutes'
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

		if not group_id:
			group_id = 'all'
		if group_id != 'all':
			group_id = int(group_id)

		return Markup(render_template('pimpy/api/side_menu.htm',
			groups=groups, group_id=group_id, personal=personal,
			type=type, endpoints=endpoints))

	@staticmethod
	def get_tasks(group_id, personal):
		if not GroupPermissionAPI.can_read('pimpy'):
			abort(403)
		if not current_user:
			flash('Current_user not found')
			return redirect(url_for('pimpy.view_tasks'))
		# TODO: only return tasks with status != completed

		list_items = {}

		if personal:
			if group_id == 'all':
				for group in UserAPI.get_groups_for_current_user():
					list_users = {}
					items = []
					for task in group.tasks:
						if current_user in task.users:
							items.append(task)
					if len(items):
						list_users[current_user.first_name + " " + current_user.last_name] = items
					if len(list_users):
						list_items[group.name] = list_users
			else:
				tasks = Task.query.filter(Task.group_id==group_id).all()
				items = []
				list_users = {}
				for task in tasks:
					if current_user in task.users:
						items.append(task)
				if len(items):
					list_users[current_user.first_name + " " + current_user.last_name] = items
				if len(list_users):
					list_items[Group.query.filter(Group.id==group_id).first().name] = list_users

				#group_name = Group.query.filter(Group.id==group_id).first().name
				#list_items[group_name] = []
				#for task in query.all():
				#	for u in task.users:
				#		if u.id == current_user.id:
				#			list_items[group_name].append(task)

		else:
			if group_id == 'all':
				for group in UserAPI.get_groups_for_current_user():
					list_users = {}
					for user in group.users:
						items = []
						for task in group.tasks:
							if user in task.users:
								items.append(task)
						if len(items):
							list_users[user.first_name + " " + user.last_name] = items
					if len(list_users):
						list_items[group.name] = list_users

			else:
				group = Group.query.filter(Group.id==group_id).first()
				list_users = {}
				for user in group.users:
					items = []
					for task in group.tasks:
						if user in task.users:
							items.append(task)
					if len(items):
						list_users[user.first_name + " " + user.last_name] = items
				if len(list_users):
					list_items[group.name] = list_users

		# remove those list items that have been set to checked and removed
		for group_header in list_items:
			for user_header in list_items[group_header]:
				list_items[group_header][user_header] = filter(lambda x: x.status < 4, list_items[group_header][user_header])

		return Markup(render_template('pimpy/api/tasks.htm',
			list_items=list_items, type='tasks', group_id=group_id,
			personal=personal))

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
			query = Minute.query.filter(Minute.group_id==group_id).order_by(Minute.minute_date.desc())
			list_items[Group.query.filter(Group.id==group_id).first().name] = query.all()
		# this should be done with a sql in statement, or something, but meh
		else:
			for group in current_user.groups:
				list_items[group.name] = Minute.query.filter(Minute.group_id==group.id).all()

		return Markup(render_template('pimpy/api/minutes.htm',
			list_items=list_items, type='minutes', group_id=group_id))

	@staticmethod
	def get_minute(group_id, minute_id):
		"""
		Load (and thus view) specifically one minute
		"""
		if not GroupPermissionAPI.can_read('pimpy'):
			abort(403)
		if not current_user:
			flash('Current_user not found')
			return redirect(url_for('pimpy.view_minutes'))

		list_items = {}
		query = Minute.query.filter(Minute.id==minute_id)
		group = Group.query.filter(Group.id==group_id).first()
		list_items[group.name] = query.all()

		return Markup(render_template('pimpy/api/minutes.htm',
			list_items=list_items, type='minutes', group_id=group_id))

	@staticmethod
	def update_content(task_id, content):
		"""
		Update the content of the task with the given id
		"""
		task = Task.query.filter(Task.id==task_id).first()
		task.content = content
		db.session.commit()
		return True, "The task is edited sucessfully"

	@staticmethod
	def update_title(task_id, title):
		"""
		Update the title of the task with the given id
		"""
		task = Task.query.filter(Task.id==task_id).first()
		task.title = title
		db.session.commit()
		return True, "The task is edited sucessfully"

	@staticmethod
	def update_users(task_id, comma_sep_users):
		"""
		Update the users of the task with the given id
		"""
		task = Task.query.filter(Task.id==task_id).first()
		users, message = PimpyAPI.get_list_of_users_from_string(task.group_id,
			comma_sep_users)
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


