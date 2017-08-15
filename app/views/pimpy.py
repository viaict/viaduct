from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from app import db
from flask_babel import _

from flask_login import current_user

from app.forms.pimpy import AddTaskForm, AddMinuteForm
from app.utils.pimpy import PimpyAPI
from app.utils.module import ModuleAPI
from app.models.pimpy import Task
from app.models.group import Group

# from app.utils import copernica


blueprint = Blueprint('pimpy', __name__, url_prefix='/pimpy')


@blueprint.route('/minutes/', methods=['GET', 'POST'])
@blueprint.route('/minutes/<int:group_id>', methods=['GET', 'POST'])
def view_minutes(group_id=None):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    return PimpyAPI.get_minutes(group_id)


@blueprint.route('/archive/', methods=['GET', 'POST'])
@blueprint.route('/archive/<int:group_id>', methods=['GET', 'POST'])
def view_minutes_in_date_range(group_id=None):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)

    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    start_date = request.form['start_date']
    end_date = request.form['end_date']
    return PimpyAPI.get_minutes_in_date_range(group_id, start_date, end_date)


@blueprint.route('/task_archive/', methods=['GET', 'POST'])
@blueprint.route('/task_archive/<int:group_id>', methods=['GET', 'POST'])
def view_tasks_in_date_range(group_id=None):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    # group_id = request.form['group_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    return PimpyAPI.get_tasks_in_date_range(
        group_id, False, start_date, end_date)


@blueprint.route('/minutes/single/<int:minute_id>/')
@blueprint.route('/minutes/single/<int:minute_id>/<int:line_number>')
def view_minute(minute_id=0, line_number=-1):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)

    return PimpyAPI.get_minute(minute_id, line_number)


@blueprint.route('/minutes/single/<int:minute_id>/raw')
def view_minute_raw(minute_id):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)

    return (PimpyAPI.get_minute_raw(minute_id),
            {'Content-Type': 'text/plain; charset=utf-8'})


@blueprint.route('/tasks/', methods=['GET', 'POST'])
@blueprint.route('/tasks/<int:group_id>/', methods=['GET', 'POST'])
def view_tasks(group_id=None):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    return PimpyAPI.get_tasks(group_id, False)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/', methods=['GET', 'POST'])
@blueprint.route('/tasks/me/<int:group_id>/', methods=['GET', 'POST'])
def view_tasks_personal(group_id=None):
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    return PimpyAPI.get_tasks(group_id, True)


@blueprint.route('/tasks/update_status/', methods=['GET', 'POST'])
def update_task_status():
    if not ModuleAPI.can_write('pimpy'):
        return abort(403)
    task_id = request.form.get('task_id', 0, type=int)
    new_status = request.form.get('new_status', 0, type=int)

    task = Task.query.get(task_id)

    print(task_id)

    if not task:
        return jsonify(success=False, message="Task does not exist"), 404
    else:
        if not task.update_status(new_status):
            return jsonify(success=False,
                           message="Invalid data"), 400

        # for user in task.users:
        #     copernica_data = {
        #         "Actiepunt": task.title,
        #         "Status": task.get_status_string(),
        #     }
        #     copernica.update_subprofile(copernica.SUBPROFILE_TASK,
        #                                 user.id, task.base32_id(),
        #                                 copernica_data)

        db.session.commit()

    return jsonify(success=True, status=task.get_status_color())


@blueprint.route('/tasks/add/', methods=['GET', 'POST'])
@blueprint.route('/tasks/add/<int:group_id>', methods=['GET', 'POST'])
def add_task(group_id=None):
    if not ModuleAPI.can_write('pimpy'):
        return abort(403)
    if group_id is not None and not current_user.member_of_group(group_id):
        return abort(403)

    form = AddTaskForm(request.form, default=group_id)
    if request.method == 'POST':
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
                form.group.data,
                form.users.data, form.line.data, -1, form.status.data)

        if result:
            flash('De taak is succesvol aangemaakt!', 'success')
            return redirect(url_for('pimpy.view_tasks',
                                    group_id=form.group.data))

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
def edit_task(task_id=-1):
    if not ModuleAPI.can_write('pimpy'):
        return abort(403)
    if task_id is '' or task_id is -1:
        flash('Taak niet gespecificeerd.')
        return redirect(url_for('pimpy.view_tasks', group_id=None))

    name = request.form['name']
    if name == "content":
        result, message = PimpyAPI.update_content(
            task_id, request.form['value'])
    elif name == "title":
        result, message = PimpyAPI.update_title(
            task_id, request.form['value'])
    elif name == "users":
        result, message = PimpyAPI.update_users(
            task_id, request.form['value'])

    status_code = 200 if result else 400

    return jsonify(result=result, message=message), status_code


@blueprint.route('/minutes/add/', methods=['GET', 'POST'])
@blueprint.route('/minutes/add/<int:group_id>', methods=['GET', 'POST'])
def add_minute(group_id=None):
    if not ModuleAPI.can_write('pimpy'):
        return abort(403)
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
                # for user in task.users:
                #     copernica_data = {
                #         "viaductID": task.base32_id(),
                #         "Actiepunt": task.title,
                #         "Status": task.get_status_string(),
                #         "Groep": task.group.name,
                #     }
                #     copernica.add_subprofile(
                #         copernica.SUBPROFILE_TASK, user.id, copernica_data)
                for done in dones:
                    if done.group_id == group.id and done.update_status(4):
                        valid_dones.append(done)
                    else:
                        flash(_("Found invalid DONE task: %s").format(
                            done.base32_id()), 'danger')

                # for user in done.users:
                #     copernica_data = {
                #         "Actiepunt": task.title,
                #         "Status": task.get_status_string(),
                #     }
                #     copernica.update_subprofile(copernica.SUBPROFILE_TASK,
                #                                 user.id, task.base32_id(),
                #                                 copernica_data)

                for remove in removes:
                    if remove.group_id == group.id and remove.update_status(5):
                        valid_removes.append(remove)
                    else:
                        flash(_("Found invalid REMOVE task: %s").format(
                            remove.base32_id()), 'danger')

                # for user in remove.users:
                #     copernica_data = {
                #         "Actiepunt": task.title,
                #         "Status": task.get_status_string(),
                #     }
                #     copernica.update_subprofile(copernica.SUBPROFILE_TASK,
                #                                 user.id, task.base32_id(),
                #                                 copernica_data)
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
