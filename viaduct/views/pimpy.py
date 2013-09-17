import datetime

from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors


from viaduct.forms.pimpy import AddTaskForm, AddMinuteForm, EditTaskForm
from viaduct.api.pimpy import PimpyAPI
from viaduct.models.pimpy import Minute, Task

from flask.ext.login import current_user

from viaduct.models.user import User
from viaduct.models.group import Group

from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')

@blueprint.route('/minutes/', methods=['GET', 'POST'])
@blueprint.route('/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	if not GroupPermissionAPI.can_read('pimpy'):
		return abort(403)
	return PimpyAPI.get_minutes(group_id)

@blueprint.route('/minutes/<group_id>/<minute_id>')
def view_minute(group_id='all', minute_id=0):
	if not GroupPermissionAPI.can_read('pimpy'):
		return abort(403)
	return PimpyAPI.get_minute(group_id, minute_id)

@blueprint.route('/tasks/', methods=['GET', 'POST'])
@blueprint.route('/tasks/<group_id>', methods=['GET', 'POST'])
def view_tasks(group_id='all'):
	if not GroupPermissionAPI.can_read('pimpy'):
		return abort(403)
	return PimpyAPI.get_tasks(group_id, False)

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/<group_id>/', methods=['GET', 'POST'])
def view_tasks_personal(group_id='all'):
	if not GroupPermissionAPI.can_read('pimpy'):
		return abort(403)
	return PimpyAPI.get_tasks(group_id, True)

@blueprint.route('/tasks/update_status/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/update_status/', methods=['GET', 'POST'])
def update_task_status():
	if not GroupPermissionAPI.can_write('pimpy'):
		return abort(403)
	task_id = request.args.get('task_id', 0, type=int)
	new_status = request.args.get('new_status', 0, type=int)

	query = Task.query
	query = query.filter(Task.id==task_id)
	list_items = query.all()
	for task in list_items:
		task.update_status(new_status)
	return jsonify(status=task.get_status_color())

@blueprint.route('/tasks/update/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/update/', methods=['GET', 'POST'])
def update_task():
	if not GroupPermissionAPI.can_write('pimpy'):
		return abort(403)


@blueprint.route('/tasks/add/<string:group_id>', methods=['GET', 'POST'])
def add_task(group_id='all'):
	if not GroupPermissionAPI.can_write('pimpy'):
		return abort(403)
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
		if form.name.data == "":
			message = "Name is required"
		#elif form.content.data == "":
		#	message = "More info is required"
		#elif request.form['deadline'] == "":
		#	message = "Deadline is required"
		elif form.group == "":
			message = "Group is required"
		elif form.users.data == "":
			message = "A minimum of 1 user is required"

		result = message == ""

		if result:
			result, message = PimpyAPI.commit_task_to_db(form.name.data,
				form.content.data, request.form['deadline'],
				form.group.data, form.users.data, form.line.data, -1,
				form.status.data)

		if result:
			flash('The task is added successfully')
			return redirect(url_for('pimpy.view_tasks', group_id=form.group.data))

		else:
			flash(message)

	group = Group.query.filter(Group.id==group_id).first()
	form.load_groups(current_user.groups.all())

	return render_template('pimpy/add_task.htm', group=group,
		group_id=group_id, type='tasks', form=form)

@blueprint.route('/tasks/edit/', methods=['GET', 'POST'])
@blueprint.route('/tasks/edit/<string:task_id>', methods=['GET', 'POST'])
def edit_task(task_id=-1):
	if not GroupPermissionAPI.can_write('pimpy'):
		return abort(403)
	if task_id == '' or task_id == -1:
		flash('task not specified')
		return redirect(url_for('pimpy.view_tasks', group_id='all'))

	if request.method == 'POST':
		name = request.form['name']
		if name == "content":
			result, message = PimpyAPI.update_content(task_id, request.form['value'])
		elif name == "title":
			result, message = PimpyAPI.update_title(task_id, request.form['value'])
		elif name == "users":
			result, message = PimpyAPI.update_users(task_id, request.form['value'])
		elif name == "deadline":
			result, message = PimpyAPI.update_deadline(task_id, request.form['value'])

		return message


	group = Group.query.filter(Group.id==task.group_id).first()
	form.load_groups(current_user.groups.all())
	return render_template('pimpy/edit_task.htm', group=group,
		group_id=group.id, type='tasks', form=form)


@blueprint.route('/minutes/add/<string:group_id>', methods=['GET', 'POST'])
def add_minute(group_id='all'):
	if not GroupPermissionAPI.can_write('pimpy'):
		return abort(403)
	if group_id == '':
		groud_id = 'all'
	group = Group.query.filter(Group.id==group_id).first()

	form = AddMinuteForm(request.form)
	if request.method == 'POST':

		# validate still does not work
		message = ""
		if form.content.data == "":
			message = "Content is required"
		elif request.form['date'] == "":
			message = "Date is required"
		elif form.group == "":
			message = "Group is required"

		result = message == ""

		if result:
			result, message = PimpyAPI.commit_minute_to_db(form.content.data,
				request.form['date'], form.group.data)
			if result and form.parse_tasks.data:
				tasks, dones, removes = PimpyAPI.parse_minute(form.content.data,
					form.group.data, message)
				for task in tasks:
					db.session.add(task)
				for done in dones:
					done.update_status(4)
				for remove in removes:
					remove.update_status(5)
				db.session.commit()
				flash('The minute has been parsed:')

				return render_template('pimpy/view_parsed_tasks.htm',
					tasks=tasks, dones=dones, removes=removes)

		if result:
			flash('The minute is added successfully')
			return redirect(url_for('pimpy.view_minutes', group_id=form.group.data))
		else:
			flash(message)

	form.load_groups(current_user.groups.all())

	return render_template('pimpy/add_minute.htm', group=group,
		group_id=group_id, type='minutes', form=form)

