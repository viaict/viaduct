import datetime

from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from flask_babel import _
from flask_login import current_user

from app import db, Roles, app
from app.decorators import require_role
from app.exceptions import ValidationException
from app.forms.pimpy import AddTaskForm, AddMinuteForm
from app.service import pimpy_service
from app.utils.pimpy import PimpyAPI
from app.models.pimpy import Task
from app.models.group import Group
# from app.utils import copernica

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

    df = app.config['DATE_FORMAT']
    start_date = datetime.datetime.strptime(start_date, df)
    end_date = datetime.datetime.strptime(end_date, df)

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

    list_items = {minute.group.name: [minute]}
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
        tasks_rel = pimpy_service.get_all_tasks_for_user(current_user)

    return render_template('pimpy/api/tasks.htm',
                           personal=False,
                           group_id=group_id,
                           tasks_rel=tasks_rel,
                           type='tasks',
                           status_meanings=status_meanings,
                           title='PimPy')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/<int:group_id>/', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_READ)
def view_tasks_personal(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    status_meanings = Task.get_status_meanings()

    if group_id is not None:
        tasks_rel = pimpy_service.get_all_tasks_for_group(group_id)
    else:
        tasks_rel = pimpy_service.get_all_tasks_for_user(current_user)

    return render_template('pimpy/api/tasks.htm',
                           personal=False,
                           group_id=group_id,
                           tasks_rel=tasks_rel,
                           type='tasks',
                           status_meanings=status_meanings,
                           title='PimPy')


@blueprint.route('/task_archive/', methods=['GET', 'POST'])
@blueprint.route('/task_archive/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_READ)
def view_tasks_in_date_range(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    # group_id = request.form['group_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    df = app.config['DATE_FORMAT']
    start_date = datetime.datetime.strptime(start_date, df)
    end_date = datetime.datetime.strptime(end_date, df)

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
            pimpy_service.update_status(current_user, task, new_status)
        except ValidationException as e:
            return jsonify(success=False, message=e.detail), 400

    return jsonify(success=True, status=task.get_status_color())


@blueprint.route('/tasks/add/', methods=['GET', 'POST'])
@blueprint.route('/tasks/add/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_WRITE)
def add_task(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    form = AddTaskForm(request.form, default=group_id)
    if request.method == 'POST':
        # TODO: use wtforms validation
        message = None
        if form.name.data == "":
            message = "Naam is vereist"
        elif form.group == "":
            message = "Groep is vereist"
        elif form.users.data == "":
            message = "Minimaal 1 gebruiker is vereist"

        if not message:
            try:
                pimpy_service.add_task(
                    form.name.data, form.content.data, int(form.group.data),
                    form.users.data, form.line.data, -1, form.status.data)

                flash('De taak is succesvol aangemaakt!', 'success')

                return redirect(url_for('pimpy.view_tasks',
                                        group_id=form.group.data))
            except ValidationException as e:
                flash(e.detail)

        else:
            flash(message, 'danger')

    group = Group.query.filter(Group.id == group_id).first()
    form.load_groups(current_user.groups)
    form.load_status(Task.status_meanings)

    return render_template('pimpy/add_task.htm', group=group,
                           group_id=group_id, type='tasks', form=form,
                           title='PimPy')


@blueprint.route('/tasks/edit/', methods=['POST'])
@blueprint.route('/tasks/edit/<string:task_id>', methods=['POST'])
@require_role(Roles.PIMPY_WRITE)
def edit_task(task_id=-1):
    if task_id is '' or task_id is -1:
        flash('Taak niet gespecificeerd.')
        return redirect(url_for('pimpy.view_tasks', group_id=None))

    name = request.form['name']
    value = request.form['value']

    if name in ('content', 'title', 'users'):
        pimpy_service.edit_task_property(current_user, task_id, name, value)
    else:
        abort(400)

    return jsonify(result=200, message='ok'), 200


@blueprint.route('/minutes/add/', methods=['GET', 'POST'])
@blueprint.route('/minutes/add/<int:group_id>', methods=['GET', 'POST'])
@require_role(Roles.PIMPY_WRITE)
def add_minute(group_id=None):
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    form = AddMinuteForm(request.form, default=group_id)
    if request.method == 'POST':

        group = Group.query.get(form.group.data)

        # validate still does not work
        message = ""
        if form.content.data == "":
            message = "Content is vereist"
        elif request.form['date'] == "":
            message = "Datum is vereist"
        elif form.group == "":
            message = "Groep is vereist"

        result = message == ""

        if result:
            result, message = PimpyAPI.commit_minute_to_db(
                form.content.data, request.form['date'], form.group.data)
            if result and form.parse_tasks.data:
                tasks, dones, removes = PimpyAPI.parse_minute(
                    form.content.data, form.group.data, message)

                valid_dones = []
                valid_removes = []

                for task in tasks:
                    db.session.add(task)

                for done in dones:
                    if done.group_id == group.id and done.update_status(4):
                        valid_dones.append(done)
                    else:
                        flash(_("Found invalid DONE task: %s").format(
                            done.base32_id()), 'danger')

                for remove in removes:
                    if remove.group_id == group.id and remove.update_status(5):
                        valid_removes.append(remove)
                    else:
                        flash(_("Found invalid REMOVE task: %s").format(
                            remove.base32_id()), 'danger')

                db.session.commit()

                flash('De notulen zijn verwerkt!', 'success')

                return render_template('pimpy/view_parsed_tasks.htm',
                                       tasks=tasks, dones=valid_dones,
                                       group_id=group_id,
                                       removes=valid_removes, title='PimPy')
        else:
            flash(message, 'danger')

    form.load_groups(current_user.groups)

    return render_template('pimpy/add_minute.htm', group_id=group_id,
                           type='minutes', form=form, title='PimPy')
