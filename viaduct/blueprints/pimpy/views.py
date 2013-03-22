from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

#<<<<<<< HEAD:viaduct/blueprints/pimpy/views.py
#blueprint = Blueprint('pimpy', __name__)
#
#@blueprint.route('/pimpy/', methods=['GET', 'POST'])
#def view_page(minutesOrTasks='all', groups=""):
#	return render_template('pimpy/view_page.htm')
#=======
from api import PimpyAPI

module = Blueprint('pimpy', __name__)

@module.route('/pimpy/', methods=['GET', 'POST'])
def view_page():
	return render_template('pimpy/view_page.htm', personal=True,
	group_id='all', type='minutes')

@module.route('/pimpy/minutes/', methods=['GET', 'POST'])
@module.route('/pimpy/minutes/<int:group_id>', methods=['GET', 'POST'])
def view_minutes(group_id='all'):
	return PimpyAPI.get_minutes(group_id)

@module.route('/pimpy/tasks/', methods=['GET', 'POST'])
@module.route('/pimpy/tasks/<int:group_id>', methods=['GET', 'POST'])
@module.route('/pimpy/tasks/me', methods=['GET', 'POST'], defaults={'personal': True})
@module.route('/pimpy/tasks/me/<int:group_id>', methods=['GET', 'POST'], defaults={'personal': True})
def view_tasks(group_id='all', personal=False):
	return PimpyAPI.get_tasks(group_id, personal)
#>>>>>>> should commit to be sure?:viaduct/pimpy/views.py

@blueprint.route('/pimpjo/', methods=['GET', 'POST'])
def test():
	return render_template('activity/create.htm')
