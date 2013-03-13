from flask import render_template, request, Markup

from viaduct.pimpy.models import Task, Minute
from viaduct.page.models import Page
from flask.ext.login import current_user

class PimpyAPI:
	@staticmethod
	def get_navigation_menu():
		print "api called"
		path = request.path
		page = Page.query.filter(Page.path==path).first()
		groups = current_user.groups.all()

		current_group = 'administrators'
		#request.args.get('group', '') =

		return Markup(render_template('pimpy/side_menu.htm',
			page=page, path=path, groups=groups, current_group=current_group))

