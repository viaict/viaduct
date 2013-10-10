from flask import make_response
import csv, os, random, bcrypt
from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint
from flask.ext.login import current_user

from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.forms.custom_form import CreateForm
from viaduct.models.user import User
from viaduct.models.group import Group
from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('custom_form', __name__)

@blueprint.route('/forms/', methods=['GET', 'POST'])
@blueprint.route('/forms/page/<int:page>', methods=['GET', 'POST'])
def view(page=1):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_forms = CustomForm.query.order_by(CustomForm.name.asc())

	return render_template('custom_form/overview.htm', custom_forms=custom_forms.paginate(page, 20, False))

@blueprint.route('/forms/download/<int:form_id>', methods=['GET', 'POST'])
def download(form_id=None):
	"""if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_form = CustomForm.query.get(form_id)

	if not custom_form:
		return abort(403)

	entries = CustomFormResult.query.filter(CustomFormResult.form_id == form_id)
	results = []
	
	for entry in entries:
		results.append([
			entry.owner.name,
			entry.owner.email,
			entry.owner.student_id,
			entry.owner.phone_nr,
			entry.owner.emergency_phone_nr
		])

	return response"""
	return "Not working"

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
		# Hide form entries from non existing users
		if not entry.owner:
			continue

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

	return render_template('custom_form/view_results.htm', custom_form=custom_form)

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
	# TODO make sure custom_form rights are set on server 
	if not GroupPermissionAPI.can_read('custom_form'):
		return abort(403)

	response = "success"

	if form_id:
		# Allow users to change their details
		#email = request.form['email'].lower()

		# Logged in user
		if current_user and current_user.id > 0:
			user = User.query.get(current_user.id)

			#user.first_name	= request.form['first_name']
			#user.last_name	= request.form['last_name']
			#user.email			= email
		else:
			# Need to be logged in
			return abort(403)

			# Check if a non-logged in user that has an account submits request
			'''
			user = User.query.filter(User.email == email).first()

			# Create a user if it does not exist yet
			if not user:
				tmp_password = ''.join(map(lambda x: random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"), range(14)))

				user = User(
					email, 
					bcrypt.hashpw(tmp_password, bcrypt.gensalt()),
					request.form['first_name'],
					request.form['last_name'],
					request.form['student_id'],
					request.form['education_id']
				)

				db.session.add(user)
				db.session.commit()

				group = Group.query.filter(Group.name=='all').first()
				group.add_user(user)

				db.session.add(group)
				db.session.commit()
	'''

	if not user:
		response = "error"
	else:
		# These fields might be there
		try :
			if request.form['phone_nr']:
				user.phone_nr	= request.form['phone_nr']

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
		except Exception :
			pass

		duplicate_test = CustomFormResult.query.filter(
			CustomFormResult.owner_id == user.id, 
			CustomFormResult.form_id == form_id
		).first()

		if duplicate_test:
			result			= duplicate_test
			result.data	= request.form['data']
			response = "edit"
		else:
			result = CustomFormResult(user.id, form_id, request.form['data'])
		
		db.session.add(user)
		db.session.commit()

		db.session.add(result)
		db.session.commit()

	return response
