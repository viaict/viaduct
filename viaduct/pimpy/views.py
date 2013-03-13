from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

module = Blueprint('pimpy', __name__)

@module.route('/pimpy/', methods=['GET', 'POST'])
def view_page(minutesOrTasks='all', groups=""):

	# haal ofwel de minutes ofwel de tasks op
	list_items = []
	#for group in current_user.groups.all():
	#	print "group id %d" % group.id
	#	if request.args.get('minutesOrTasks', '') == 'tasks':
	#		print "shall load tasks!" 
	#		list_items.extend(group.tasks.all())
	#	elif request.args.get('minutesOrTasks', '') == 'minutes':
	#		print "shall load minutes!" 
	#		list_items.extend(group.minutes.all())
	#		

	#print len(list_items)
	return render_template('pimpy/view_page.htm', list_items=list_items, page=True)

