from flask import render_template, request, Markup
from flask.ext.login import current_user

from models import Task, Minute

from viaduct.blueprints.page.models import Page

class PimpyAPI:
	"""
	TODO: check if groups are enabled for Pimpy. This has something to do with
		roles groups can have. Stephan should first fix those roles.
	"""


	@staticmethod
	def get_navigation_menu(group_id, personal, type):
		groups = current_user.groups.all()

		endpoint = 'pimpy.view_' + type

		return Markup(render_template('pimpy/api/side_menu.htm',
			groups=groups, group_id=group_id, personal=personal,
			type=type, endpoint=endpoint))

	@staticmethod
	def get_tasks(group_id, personal):

		list_items = []

		if personal:
			query = current_user.tasks
			if group_id != 'all':
				query = query.filter(Task.group_id==group_id)
			list_items.extend(query.all())
		else:
			groups = current_user.groups.all()
			for group in groups:
				list_items.extend(group.tasks.all())

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

		return Markup(render_template('pimpy/api/tasks.htm',
			list_items=list_items, type='minutes', group_id=group_id))

