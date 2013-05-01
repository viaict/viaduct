from flask import Blueprint, abort
from flask import flash, render_template, request
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from api import PimpyAPI

from viaduct.blueprints.user.models import User, UserPermission


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

@blueprint.route('/pimpy/tasks/add/<string:group_id>')
def add_task(group_id='all'):
	return PimpyAPI.add_task(group_id)

@blueprint.route('/pimpy/minutes/add/<string:group_id>')
def add_minute(group_id='all'):
	return PimpyAPI.add_minute(group_id)
