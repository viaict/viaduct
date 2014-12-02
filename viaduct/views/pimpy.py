from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from viaduct import db

from flask.ext.login import current_user

from viaduct.forms.pimpy import AddTaskForm, AddMinuteForm
from viaduct.api.pimpy import PimpyAPI
from viaduct.api.group import GroupPermissionAPI
from viaduct.models.pimpy import Task
from viaduct.models.group import Group


blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')


@blueprint.route('/archive/', methods=['GET', 'POST'])
@blueprint.route('/archive/<int:group_id>/', methods=['GET', 'POST'])
def view_task_archive(group_id='all'):
    """
    Shows all tasks ever made.
    Can specify specific group.
    No internal permission system made yet.
    Do not make routes to this module yet.
    """
    if not GroupPermissionAPI.can_read('pimpy'):
        return abort(403)
    return PimpyAPI.get_all_tasks(group_id)


@blueprint.route('/minutes/', methods=['GET', 'POST'])
@blueprint.route('/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
    if not GroupPermissionAPI.can_read('pimpy'):
        return abort(403)
    return PimpyAPI.get_minutes(group_id)


@blueprint.route('/minutes/<group_id>/<minute_id>/')
@blueprint.route('/minutes/<group_id>/<minute_id>/<line_number>')
def view_minute(group_id='all', minute_id=0, line_number=-1):
    if not GroupPermissionAPI.can_read('pimpy'):
        return abort(403)
    return PimpyAPI.get_minute(group_id, minute_id, line_number)


@blueprint.route('/tasks/', methods=['GET', 'POST'])
@blueprint.route('/tasks/<group_id>/', methods=['GET', 'POST'])
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
    query = query.filter(Task.id == task_id)
    list_items = query.all()
    for task in list_items:
        task.update_status(new_status)
    return jsonify(status=task.get_status_color())


@blueprint.route('/tasks/add/<string:group_id>', methods=['GET', 'POST'])
def add_task(group_id='all'):
    if not GroupPermissionAPI.can_write('pimpy'):
        return abort(403)
    if group_id == '':
        group_id = 'all'

    form = AddTaskForm(request.form, default=group_id)
    if request.method == 'POST':
        # FIXME: deadline is also messed up, and I do not know why

        # FIXME: validate does not seem to work :(, so we are doin' it
        # manually now
        message = ""
        if form.name.data == "":
            message = "Naam is vereist"
        elif form.group == "":
            message = "Groep is vereist"
        elif form.users.data == "":
            message = "Minimaal 1 gebruiker is vereist"

        result = message == ""

        if result:
            result, message = PimpyAPI.commit_task_to_db(
                form.name.data, form.content.data,
                request.form['deadline'], form.group.data,
                form.users.data, form.line.data, -1, form.status.data)

        if result:
            flash('De taak is succesvol aangemaakt!', 'success')
            return redirect(url_for('pimpy.view_tasks',
                                    group_id=form.group.data))

        else:
            flash(message, 'danger')

    group = Group.query.filter(Group.id == group_id).first()
    form.load_groups(current_user.groups.order_by(Group.name.asc()).all())

    return render_template('pimpy/add_task.htm', group=group,
                           group_id=group_id, type='tasks', form=form,
                           title='PimPy')


@blueprint.route('/tasks/edit/', methods=['POST'])
@blueprint.route('/tasks/edit/<string:task_id>', methods=['POST'])
def edit_task(task_id=-1):
    if not GroupPermissionAPI.can_write('pimpy'):
        return abort(403)
    if task_id is '' or task_id is -1:
        flash('Taak niet gespecificeerd.')
        return redirect(url_for('pimpy.view_tasks', group_id='all'))

    if request.method == 'POST':
        name = request.form['name']
        if name == "content":
            result, message = PimpyAPI.update_content(task_id,
                                                      request.form['value'])
        elif name == "title":
            result, message = PimpyAPI.update_title(task_id,
                                                    request.form['value'])
        elif name == "users":
            result, message = PimpyAPI.update_users(task_id,
                                                    request.form['value'])
        elif name == "deadline":
            result, message = PimpyAPI.update_deadline(task_id,
                                                       request.form['value'])

        return message


@blueprint.route('/minutes/add/<string:group_id>', methods=['GET', 'POST'])
def add_minute(group_id='all'):
    if not GroupPermissionAPI.can_write('pimpy'):
        return abort(403)
    if group_id == '':
        group_id = 'all'
    group = Group.query.filter(Group.id == group_id).first()

    form = AddMinuteForm(request.form, default=group_id)
    if request.method == 'POST':

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
                for task in tasks:
                    db.session.add(task)
                for done in dones:
                    done.update_status(4)
                for remove in removes:
                    remove.update_status(5)
                db.session.commit()
                flash('De notulen is verwerkt!', 'success')

                return render_template('pimpy/view_parsed_tasks.htm',
                                       tasks=tasks, dones=dones,
                                       removes=removes, title='PimPy')
        else:
            flash(message, 'danger')

    form.load_groups(current_user.groups.order_by(Group.name.asc()).all())

    return render_template('pimpy/add_minute.htm', group=group,
                           group_id=group_id, type='minutes', form=form,
                           title='PimPy')
