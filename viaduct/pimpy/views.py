from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

module = Blueprint('pimpy', __name__)

@module.route('/pimpy/', methods=['GET', 'POST'])
@module.route('/pimpy/<minutesOrTasks>/<groups>', methods=['GET', 'POST'])
def view_page(type='all', groups=):

	# haal 
	list_items = []
	for group in current_user.groups.all():
		if type == 'tasks'
			for task in group.minutes
				list_items.extend(minute.tasks.all())
		elif type == 'minutes'
			for minute in group.minutes
				list_items.extend(minute.tasks.all())
			

	
	return render_template('pimpy/view_page.htm', list_items=list_items, page=True, path=path)

