import os

from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint
from flask.ext.login import current_user

from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.forms.custom_form import CreateForm
from viaduct.models.user import User
from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct.api.group import GroupPermissionApi

blueprint = Blueprint('custom_form', __name__)

@blueprint.route('/forms/', methods=['GET', 'POST'])
@blueprint.route('/forms/page/<int:page>', methods=['GET', 'POST'])
def view(page=1):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_forms = CustomForm.query.order_by(CustomForm.name.asc())
	return render_template('custom_form/overview.htm', custom_forms=custom_forms.paginate(page, 20, False))

@blueprint.route('/forms/view/<int:form_id>', methods=['GET', 'POST'])
def view_single(form_id=None):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_form = CustomForm.query.get(form_id)

	if not custom_form:
		return abort(403)

	results = []
	entries = CustomFormResult.query.filter(CustomFormResult.form_id == form_id)

	from urllib import unquote_plus
	from urlparse import parse_qs

	for entry in entries:
		data = parse_qs(entry.data)

		html = '<dl>'

		for key in data:
			html += "<dt>%s" % key.replace('[]', '')

			if type(data[key]) is list:
				html += "<dd>%s" % ', '.join(data[key])
			else: 
				html += "<dd>%s" % unquote_plus(data[key])

		html += '</dl>'

		results.append({
			'owner'				: entry.owner,
			'form_entry'	: html,
		})

	custom_form.results = results

	return render_template('custom_form/view_single.htm', custom_form=custom_form)

@blueprint.route('/forms/create/', methods=['GET', 'POST'])
@blueprint.route('/forms/edit/<int:form_id>', methods=['GET', 'POST'])
def create(form_id=None):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	if form_id:
		custom_form = CustomForm.query.get(form_id)

		if not custom_form:
			abort(404)
	else:
		custom_form = CustomForm()

	form = CreateForm(request.form, custom_form)

	if request.method == 'POST':
		custom_form.name 		= form.name.data
		custom_form.origin 	= form.origin.data
		custom_form.html 		= form.html.data

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
	if not GroupPermissionAPI.can_read('custom_form'):
		return abort(403)

	# User needs to be logged in
	if current_user.id and form_id:

		response = "success"

		user = User.query.get(current_user.id)
		
		# These are definitely there
		user.first_name = request.form['first_name']
		user.last_name = request.form['last_name']
		user.email = request.form['email']
		user.phone_nr = request.form['phone_nr']
		
		# These might be there
		try :
			if request.form['noodnummer']:
				user.emergency_phone_nr = request.form['noodnummer']

			if request.form['shirt_maat']:
				user.shirt_size = request.form['shirt maat']

			if request.form['dieet[]']:
				user.diet = ', '.join(request.form['dieet[]'])
		
			if request.form['allergie/medicatie']:
				user.allergy = request.form['allergie/medicatie']

			if request.form['geslacht']:
				user.gender = request.form['geslacht']
		
		# TODO
		except Exception :
			pass

		duplicate_test = CustomFormResult.query.filter(
			CustomFormResult.owner_id == current_user.id, 
			CustomFormResult.form_id == form_id).first()

		if duplicate_test:
			result = duplicate_test
			result.data = request.form['data']
		
			response = "edit"
		else:
			result = CustomFormResult(current_user.id, form_id, request.form['data'])
		
		db.session.add(user)
		db.session.commit()

		db.session.add(result)
		db.session.commit()
	else :
		response = "error"

	return response
