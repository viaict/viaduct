from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from api import PimpyAPI

blueprint = Blueprint('pimpy', __name__)

@blueprint.route('/pimpy/', methods=['GET', 'POST'])
def view_page():
	return render_template('pimpy/view_page.htm', personal=True,
	group_id='all', type='minutes')

@blueprint.route('/pimpy/minutes/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/minutes/<group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	return PimpyAPI.get_minutes(group_id)

@blueprint.route('/pimpy/tasks/', methods=['GET', 'POST'])
@blueprint.route('/pimpy/tasks/<group_id>', methods=['GET', 'POST'])
@blueprint.route('/pimpy/tasks/me', methods=['GET', 'POST'], defaults={'personal': True})
@blueprint.route('/pimpy/tasks/me/<group_id>', methods=['GET', 'POST'], defaults={'personal': True})
def view_tasks(group_id='all', personal=False):
	return PimpyAPI.get_tasks(group_id, personal)

@blueprint.route('/pimpy/', methods=['GET', 'POST'])
def view_page(minutesOrTasks='all', groups=""):
	return render_template('pimpy/view_page.htm')
