from flask import Blueprint, abort
from flask import render_template, jsonify
from jinja2.exceptions import TemplateNotFound

from flask_login import current_user

from app import app
from app.utils.module import ModuleAPI
from app.models.pimpy import Task, TaskUserRel
from app.models.group import Group

# from app.utils import copernica


blueprint = Blueprint('apimpy', __name__, url_prefix='/apimpy')


@blueprint.route('/', methods=['GET'])
def pimpy():
    if not ModuleAPI.can_read('pimpy'):
        return abort(403)
    return render_template('pimpy/pimpy.htm')


@blueprint.route('/template/<path:template>/', methods=['GET'])
def angular(template=''):
    try:
        return render_template('pimpy/' + template)
    except TemplateNotFound as e:
        return jsonify(error='Template not found'), 404


@blueprint.route('/api/groups/', methods=['GET'])
def groups():
    if not ModuleAPI.can_read('pimpy'):
        return jsonify(error='User not logged in'), 403
    groups = [group.name for group in current_user.groups.all()]
    return jsonify(groups), 200


@blueprint.route('/api/tasks/', methods=['GET'])
def tasks(personal=False):
    if not ModuleAPI.can_read('pimpy'):
        return jsonify(error='User not logged in'), 403
    groups = current_user.groups.all()
    groups = map(lambda x: x.id, groups)
    tasks = Task.query.filter(Task.group_id.in_(groups))
    tasks = tasks.filter(~Task.status.in_((4, 5)))
    tasks = tasks.join(Group).order_by(Group.name.asc(), Task.id.asc())
    if personal == 1:
        tasks = tasks.join(TaskUserRel)\
            .filter(TaskUserRel.user == current_user)
    tasks = tasks.all()
    # print([user.name for user in tasks[0].users.all()])
    tasks = [{"id": task.id,
              "b32id": task.base32_id(),
              "title": task.title,
              "group": task.group.name,
              "users": [user.name for user in task.users.all()],
              "status": task.get_status_color()} for task in tasks]
    return jsonify(tasks), 200


@blueprint.route('/api/tasks/<int:task_id>/', methods=['GET'])
def get_task(task_id=0):
    # if not ModuleAPI.can_read('pimpy'):
    #     return jsonify(error='User not logged in'), 403
    task = Task.query.get(task_id)
    # task.group.has_user(current_user)
    # print([user.name for user in tasks[0].users.all()])
    task = {"id": task.id,
            "b32id": task.base32_id(),
            "title": task.title,
            "content": task.content,
            "minute_id": task.minute_id,
            "line": task.line,
            "group": task.group.name,
            "users": [user.name for user in task.users.all()],
            "timestamp": task.timestamp.strftime(
                app.config['DATE_FORMAT']),
            "status": task.status}
    return jsonify(task), 200
