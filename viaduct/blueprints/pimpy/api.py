from flask import render_template, request, Markup
from flask.ext.login import current_user

from models import Task, Minute

from viaduct.blueprints.page.models import Page

class PimpyAPI:
	@staticmethod
	def get_navigation_menu():
		groups = current_user.groups.all()
		current_group = 'administrators'
		group = request.args.get('group', '')
		type = request.args.get('type', '')

		return Markup(render_template('pimpy/api/side_menu.htm',
			groups=groups, current_group=current_group, type=type))

	@staticmethod
	def get_minutes_or_tasks():
		groups = current_user.groups.all()
		current_group = 'administrators'
		group = request.args.get('group', '')
		type = request.args.get('type', '')


		list_items = []
		for group in current_user.groups.all():
			print "group id %d" % group.id
			if request.args.get('type', '') == 'tasks':
				print "shall load tasks!" 
				list_items.extend(group.tasks)
			elif request.args.get('type', '') == 'minutes':
				print "shall load minutes!" 
				list_items.extend(group.minutes)

		url_part = "tasks" if request.args.get('minutesOrTasks', '') == 'tasks' else "minutes"
		return Markup(render_template('pimpy/api/%s.htm' % url_part,
				list_items=list_items, groups=groups, current_group=current_group, type=type))
