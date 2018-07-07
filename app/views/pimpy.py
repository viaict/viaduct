import datetime

from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from flask_login import current_user

from app import Roles, constants
from app.decorators import require_role
from app.exceptions import ValidationException, ResourceNotFoundException, \
    InvalidMinuteException
from app.forms.pimpy import AddTaskForm, AddMinuteForm
from app.models.pimpy import Task
from app.service import pimpy_service, group_service

blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')


@blueprint.route('/minutes/', methods=['GET', 'POST'])
@blueprint.route('/minutes/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_READ)
def view_minutes(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    if group_id:
        list_items = pimpy_service.get_all_minutes_for_group(group_id)
    else:
        list_items = pimpy_service.get_all_minutes_for_user(current_user)

    return render_template('pimpy/api/minutes.htm',
                           list_items=list_items, type='minutes',
                           group_id=group_id, line_number=-1,
                           title='PimPy')


@blueprint.route('/archive/', methods=['POST'])
@blueprint.route('/archive/<int:group_id>', methods=['POST'])
@require_role(Roles.PIMPY_READ)
def view_minutes_in_date_range(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    start_date = request.form['start_date']
    end_date = request.form['end_date']

    start_date = datetime.datetime.strptime(start_date, constants.DATE_FORMAT)
    end_date = datetime.datetime.strptime(end_date, constants.DATE_FORMAT)

    if group_id:
        list_items = pimpy_service.get_all_minutes_for_group(group_id, (
            start_date, end_date))
    else:
        list_items = pimpy_service.get_all_minutes_for_user(current_user)

    return render_template('pimpy/api/minutes.htm',
                           list_items=list_items, type='minutes',
                           group_id=group_id, line_number=-1,
                           title='PimPy')


@blueprint.route('/minutes/single/<int:minute_id>/')
@blueprint.route('/minutes/single/<int:minute_id>/<int:line_number>')
@require_role(Roles.PIMPY_READ)
def view_minute(minute_id=0, line_number=-1):
    minute = pimpy_service.find_minute_by_id(minute_id)
    if not minute:
        abort(404)

    list_items = [{
        'group_name': minute.group.name,
        'minutes': [minute]
    }]

    tag = "%dln%d" % (minute.id, int(line_number))

    return render_template('pimpy/api/minutes.htm', list_items=list_items,
                           type='minutes', group_id=minute.group.id,
                           line_number=line_number, tag=tag,
                           title='PimPy')


@blueprint.route('/minutes/single/<int:minute_id>/raw')
@require_role(Roles.PIMPY_READ)
def view_minute_raw(minute_id):
    minute = pimpy_service.find_minute_by_id(minute_id)
    if not minute:
        abort(404)

    return minute.content, {'Content-Type': 'text/plain; charset=utf-8'}


@blueprint.route('/tasks/', methods=['GET', 'POST'])
@blueprint.route('/tasks/<int:group_id>/', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_READ)
def view_tasks(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    status_meanings = Task.get_status_meanings()

    if group_id is not None:
        tasks_rel = pimpy_service.get_all_tasks_for_group(group_id)
    else:
        tasks_rel = pimpy_service.get_all_tasks_for_users_in_groups_of_user(
            current_user)

    return render_template('pimpy/api/tasks.htm',
                           personal=False,
                           group_id=group_id,
                           tasks_rel=tasks_rel,
                           type='tasks',
                           status_meanings=status_meanings,
                           title='PimPy')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/tasks/self/', methods=['GET', 'POST'])
@blueprint.route('/tasks/self/<int:group_id>/', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_READ)
def view_tasks_personal(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    status_meanings = Task.get_status_meanings()

    if group_id is not None:
        tasks_rel = pimpy_service.get_all_tasks_for_group(group_id,
                                                          user=current_user)
    else:
        tasks_rel = pimpy_service.get_all_tasks_for_user(current_user)

    return render_template('pimpy/api/tasks.htm',
                           personal=True,
                           group_id=group_id,
                           tasks_rel=tasks_rel,
                           type='tasks',
                           status_meanings=status_meanings,
                           title='PimPy')


@blueprint.route('/task_archive/', methods=['POST'])
@blueprint.route('/task_archive/<int:group_id>', methods=['POST'])
@require_role(Roles.PIMPY_READ)
def view_tasks_in_date_range(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    start_date = request.form['start_date']
    end_date = request.form['end_date']

    start_date = datetime.datetime.strptime(start_date, constants.DATE_FORMAT)
    end_date = datetime.datetime.strptime(end_date, constants.DATE_FORMAT)

    date_tuple = (start_date, end_date)

    status_meanings = Task.get_status_meanings()

    if group_id is not None:
        tasks_rel = pimpy_service.get_all_tasks_for_group(group_id, date_tuple)
    else:
        tasks_rel = pimpy_service.get_all_tasks_for_user(current_user,
                                                         date_tuple)

    return render_template('pimpy/api/tasks.htm',
                           personal=False,
                           group_id=group_id,
                           tasks_rel=tasks_rel,
                           type='tasks',
                           status_meanings=status_meanings,
                           title='PimPy')


@blueprint.route('/tasks/update_status/', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_WRITE)
def update_task_status():
    task_id = request.form.get('task_id', 0, type=int)
    new_status = request.form.get('new_status', 0, type=int)

    task = pimpy_service.find_task_by_id(task_id)
    if not task:
        return jsonify(success=False, message="Task does not exist"), 404
    else:
        try:
            pimpy_service.set_task_status(current_user, task, new_status)
        except ValidationException as e:
            return jsonify(success=False, message=e.details), 400

    return jsonify(success=True, status=task.get_status_color())


@blueprint.route('/tasks/add/', methods=['GET', 'POST'])
@blueprint.route('/tasks/add/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_WRITE)
def add_task(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    # Set the group as default
    try:
        group = group_service.get_group_by_id(group_id)
    except ResourceNotFoundException:
        group = None
    form = AddTaskForm(request.form, group=group)

    if form.validate_on_submit():
        try:
            pimpy_service.add_task_by_user_string(
                form.name.data, form.content.data, form.group.data.id,
                form.users.data, None, None, form.status.data)

            flash('De taak is succesvol aangemaakt!', 'success')
            return redirect(url_for('pimpy.view_tasks',
                                    group_id=form.group.data.id))
        except ValidationException as e:
            # TODO fix translations outside of service.
            flash(e.details)

    return render_template('pimpy/add_task.htm', group=group,
                           group_id=group_id, type='tasks', form=form,
                           title='PimPy')


@blueprint.route('/minutes/add/', methods=['GET', 'POST'])
@blueprint.route('/minutes/add/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_WRITE)
def add_minute(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    # Set the current group as default.
    try:
        group = group_service.get_group_by_id(group_id)
    except ResourceNotFoundException:
        group = None
    form = AddMinuteForm(request.form, group=group)

    if form.validate_on_submit():
        minute_group = group_service.get_group_by_id(form.group.data.id)

        try:
            minute = pimpy_service.add_minute(
                content=form.content.data, date=form.date.data,
                group=minute_group)
        except InvalidMinuteException as e:
            return render_template('pimpy/add_minute.htm', group_id=group_id,
                                   type='minutes', form=form, title='PimPy',
                                   invalid_lines=e.details)
        return redirect(url_for("pimpy.view_minute", minute_id=minute.id))

    return render_template('pimpy/add_minute.htm', group_id=group_id,
                           type='minutes', form=form, title='PimPy')


@blueprint.route('/tasks/edit/', methods=['POST'])
@blueprint.route('/tasks/edit/<string:task_id>', methods=['POST'])
@require_role(Roles.PIMPY_WRITE)
def edit_task(task_id=-1):
    """Ajax method for updating a task."""
    if task_id is '' or task_id is -1:
        flash('Taak niet gespecificeerd.')
        return redirect(url_for('pimpy.view_tasks', group_id=None))

    name = request.form['name']
    value = request.form['value']

    if name == 'content':
        pimpy_service.edit_task_property(current_user, task_id, content=value)
    elif name == 'title':
        pimpy_service.edit_task_property(current_user, task_id, title=value)
    elif name == 'users':
        pimpy_service.edit_task_property(current_user, task_id,
                                         users_property=value)
    else:
        jsonify(result=400, message='Unknown property'), 400

    return jsonify(result=200, message='ok'), 200
