from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

module = Blueprint('pimpy', __name__)

@module.route('/pimpy/', methods=['GET', 'POST'])
def get_page(path=''):
	return render_template('pimpy/view_page.htm', page=True, path=path)

