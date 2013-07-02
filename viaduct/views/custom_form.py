import os

from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint
from flask.ext.login import current_user

from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.forms.custom_form import CreateForm
from viaduct.models.custom_form import CustomForm, CustomFormResult

blueprint = Blueprint('custom_form', __name__)

@blueprint.route('/forms/', methods=['GET', 'POST'])
@blueprint.route('/forms/page/<int:page>', methods=['GET', 'POST'])
def view(page=1):
	custom_forms = CustomForm.query.order_by(CustomForm.name.asc())
	return render_template('custom_form/overview.htm', custom_forms=custom_forms.paginate(page, 20, False))

@blueprint.route('/forms/view/<int:form_id>', methods=['GET', 'POST'])
def view_single(form_id=None):
	custom_form = CustomForm.query.filter(CustomForm.id == form_id).first()

	if not custom_form:
		return abort(403)

	custom_form.results = CustomFormResult.query.filter(CustomFormResult.form_id == form_id)

	return render_template('custom_form/view_single.htm', custom_form=custom_form)

@blueprint.route('/forms/create/', methods=['GET', 'POST'])
@blueprint.route('/forms/edit/<int:form_id>', methods=['GET', 'POST'])
def create(form_id=None):
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if form_id:
		custom_form = CustomForm.query.filter(CustomForm.id == form_id).first()

		if not custom_form:
			abort(404)
	else:
		custom_form = CustomForm()

	form = CreateForm(request.form, custom_form)

	if request.method == 'POST':
		custom_form.name = form.name.data
		custom_form.origin = form.origin.data
		custom_form.html = form.html.data

		if custom_form.id:
			flash('You\'ve created a form successfully.', 'success')
		else:
			flash('You\'ve updated a form successfully.', 'success')

		db.session.add(custom_form)
		db.session.commit()

		return redirect(url_for('custom_form.view'))
	else:
		flash_form_errors(form)

	return render_template('custom_form/create.htm', form=form)

@blueprint.route('/forms/submit/<int:form_id>', methods=['POST'])
def submit(form_id=None):
	# User needs to be logged in

	if request.method== 'POST' and current_user.id and form_id and not request.form['mail']:

		response = "success"

		duplicate_test = CustomFormResult.query.filter(
			CustomFormResult.owner_id == current_user.id, 
			CustomFormResult.form_id == form_id).first()

		if duplicate_test:
			result = duplicate_test
			result.data = request.form['data']
		
			response = "edit"
		else:
			result = CustomFormResult(current_user.id, form_id, request.form['data'])
		
		db.session.add(result)
		db.session.commit()

		return response

	return "error"

