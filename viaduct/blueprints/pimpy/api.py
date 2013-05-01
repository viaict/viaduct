from flask import render_template, request, Markup, redirect, url_for, abort
from flask.ext.login import current_user

from models import Task, Minute

class PimpyAPI:

	@staticmethod
	def check_user_is_logged_in():
		print "_%s_ _%s_ _%s_ _%s_" % (current_user.first_name, current_user.last_name, current_user.email, current_user.is_authenticated())
		if not current_user.is_authenticated():
			abort(403)
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

		#if personal:
		#	query = current_user.tasks
		#	if group_id != 'all':
		#		query = query.filter(Task.group_id==group_id)
		#	list_items.extend(query.all())
		#else:
		#	groups = current_user.groups
		#	if group_id == 'all':
		#		groups = groups.all()
		#		for group in groups:
		#			list_items.extend(group.tasks.all())
		#	else:
		#		groups.filter(Task.group_id==group_id)
		#		list_items.extend(groups.all())

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
