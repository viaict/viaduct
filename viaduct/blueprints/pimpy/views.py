import datetime

from flask import Blueprint, abort
from flask import flash, render_template, request
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from api import PimpyAPI
from forms import AddTaskForm, AddMinuteForm
from models import Minute, Task

from flask.ext.login import current_user

from viaduct.blueprints.user.models import User, UserPermission
from viaduct.blueprints.group.models import Group



blueprint = Blueprint('pimpy', __name__)

@blueprint.route('/pimpy/', methods=['GET', 'POST'])
def view_page():
	return render_template('pimpy/view_page.htm', personal=True,
		group_id='all', type='minutes')

@blueprint.route('/pimpy/minutes/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	return PimpyAPI.get_minutes(group_id)

@blueprint.route('/pimpy/minutes/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	return PimpyAPI.get_minutes(group_id)

@blueprint.route('/pimpy/minutes/<group_id>/<minute_id>')
def view_minute(group_id='all', minute_id=0):
	return PimpyAPI.get_minute(group_id, minute_id)

@blueprint.route('/pimpy/tasks/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/tasks/<group_id>', methods=['GET', 'POST'])
def view_tasks(group_id='all'):
	return PimpyAPI.get_tasks(group_id, False)

@blueprint.route('/pimpy/tasks/me/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/tasks/me/<group_id>/', methods=['GET', 'POST'])
def view_tasks_personal(group_id='all'):
	return PimpyAPI.get_tasks(group_id, True)

@blueprint.route('/pimpy/tasks/add/<string:group_id>', methods=['GET', 'POST'])
def add_task(group_id='all'):
	if group_id == '':
		groud_id = 'all'

	form = AddTaskForm(request.form)
	if request.method == 'POST':
		# FIXME: deadline is also messed up, and I do not know why
		#if form.validate():
		#	flash("VALIDAATES!!!!")

		# FIXME: validate does not seem to work :(, so we are doin' it
		# manually now
		message = ""
		if form.name.data == None:
			message = "Name is required"
		if request.form['deadline'] == None:
			message = "Deadline is required"
		if form.group == None:
			message = "Group is required"
		if form.users.data == None:
			message = "A minimum of 1 user is required"

		result = message == ""

		if result:
			result, message = PimpyAPI.commit_task_to_db(form.name.data,
				form.content.data, request.form['deadline'],
				form.group.data, form.users.data, form.line.data, -1,
				form.status.data)
		else:
			flash(message)

		if result:
			flash("Success! %s" % message)
			# maybe redirect to the created task or something else
		else:
			flash(message)

	group = Group.query.filter(Group.id==group_id).first()
	form.load_groups(current_user.groups.all())

	return render_template('pimpy/add_task.htm', group=group,
		group_id=group_id, type='tasks', form=form)

@blueprint.route('/pimpy/minutes/add/<string:group_id>')
def add_minute(group_id='all'):
	if group_id == '':
		groud_id = 'all'
	group = Group.query.filter(Group.id==group_id).first()

	form = AddMinuteForm()

	return render_template('pimpy/add_minute.htm', group=group, group_id=group_id, type='minutes', form=form)

