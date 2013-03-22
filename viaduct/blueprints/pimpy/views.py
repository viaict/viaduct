from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

blueprint = Blueprint('pimpy', __name__)

@blueprint.route('/pimpy/', methods=['GET', 'POST'])
def view_page(minutesOrTasks='all', groups=""):
	return render_template('pimpy/view_page.htm')

@blueprint.route('/pimpjo/', methods=['GET', 'POST'])
def test():
	return render_template('activity/create.htm')
