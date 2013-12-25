from flask import make_response
import csv, os, random, bcrypt
from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint
from flask.ext.login import current_user
import datetime
from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.forms.custom_form import CreateForm
from viaduct.models.user import User
from viaduct.models.group import Group
from viaduct.models.custom_form import CustomForm, CustomFormResult, CustomFormFollower
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('custom_form', __name__)

@blueprint.route('/forms/', methods=['GET', 'POST'])
@blueprint.route('/forms/page/<int:page>', methods=['GET', 'POST'])
def view(page=1):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_forms = CustomForm.query.order_by("created")

	if current_user and current_user.id > 0:
		follows = CustomFormFollower.query.filter(CustomFormFollower.owner_id == current_user.id).all()

		ids = []

		for follow in follows:
			ids.append(follow.form_id)

		followed_forms = CustomForm.query.filter(CustomForm.id.in_(ids)).all()
	else:
		followed_forms = []
		ids = []

	# TODO Custom forms for specific groups (i.e coordinator can only see own forms)
	return render_template('custom_form/overview.htm', custom_forms=custom_forms.paginate(page, 20, False), followed_forms=followed_forms, followed_ids=ids)

@blueprint.route('/forms/view/<int:form_id>', methods=['GET', 'POST'])
def view_single(form_id=None):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	custom_form = CustomForm.query.get(form_id)

	if not custom_form:
		return abort(403)

	results = []
	entries = CustomFormResult.query.filter(CustomFormResult.form_id == form_id).order_by("created")

	from urllib import unquote_plus
	from urlparse import parse_qs

	for entry in entries:
		# Hide form entries from non existing users
		data = parse_qs(entry.data)

		html = '<dl>'

		for key in data:
			html += "<dt>%s" % key.replace('[]', '')

			if type(data[key]) is list:
				html += "<dd>%s" % ', '.join(data[key])
			else:
				html += "<dd>%s" % unquote_plus(data[key])

		html += '</dl>'

		time = entry.created.strftime("%Y-%m-%d %H:%I") if entry.created != None else ""

		results.append({
			'id'				  : entry.id,
			'owner'				: entry.owner,
			'form_entry'	: html,
			'class'				: 'class="is_reserve"' if entry.is_reserve else '',
			'has_payed'		: entry.has_payed,
			'time'				: time
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
		custom_form.max_attendants	= form.max_attendants.data

		if not form_id:
			flash('You\'ve created a form successfully.', 'success')
		else:
			flash('You\'ve updated a form successfully.', 'success')

		db.session.add(custom_form)
		db.session.commit()

		return redirect(url_for('custom_form.view'))
	else:
		flash_form_errors(form)

	return render_template('custom_form/create.htm', form=form)


@blueprint.route('/forms/remove/<int:submit_id>', methods=['POST'])
def remove_response(submit_id=None):
	response = "success"

	if not GroupPermissionAPI.can_read('custom_form'):
		return abort(403)

	# Test if user already signed up
	submission = CustomFormResult.query.filter(
		CustomFormResult.id == submit_id
	).first()

	if not submission:
		abort(404)

	db.session.delete(submission)
	db.session.commit()

	return response

@blueprint.route('/forms/submit/<int:form_id>', methods=['POST'])
def submit(form_id=None):
	# TODO make sure custom_form rights are set on server
	if not GroupPermissionAPI.can_read('custom_form'):
		return abort(403)

	response = "success"

	if form_id:
		custom_form = CustomForm.query.get(form_id)

		if not custom_form:
			abort(404)

		# Logged in user
		if current_user and current_user.id > 0:
			user = User.query.get(current_user.id)
		else:
			# Need to be logged in
			return abort(403)

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

		# Test if user already signed up
		duplicate_test = CustomFormResult.query.filter(
			CustomFormResult.owner_id == user.id,
			CustomFormResult.form_id == form_id
		).first()

		if duplicate_test:
			result			= duplicate_test
			result.data	= request.form['data']
			response = "edit"
		else:
			entries = CustomFormResult.query.filter(CustomFormResult.form_id == form_id)
			num_attendants = entries.count()

			# Check if number attendants allows another registration
			if num_attendants >= custom_form.max_attendants:
				# Create "Reserve" signup
				result = CustomFormResult(user.id, form_id, request.form['data'], True)
				response = "reserve"
			else:
				result = CustomFormResult(user.id, form_id, request.form['data'])

		db.session.add(user)
		db.session.commit()

		db.session.add(result)
		db.session.commit()

	return response

@blueprint.route('/forms/follow/<int:form_id>', methods=['GET', 'POST'])
def follow(form_id=None):
	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	# Logged in user
	if current_user and current_user.id > 0:
		user = User.query.get(current_user.id)
	else:
		# Need to be logged in
		return abort(403)

	# Unfollow if re-submitted
	follows = CustomFormFollower.query.filter(CustomFormFollower.form_id == form_id).first()

	if follows:
		response = "removed"
		db.session.delete(follows)
	else:
		response = "added"
		result = CustomFormFollower(current_user.id, form_id)
		db.session.add(result)

	db.session.commit()

	return response

@blueprint.route('/forms/has_payed/<int:submit_id>', methods=['POST'])
def has_payed(submit_id=None):
	response = "success"

	if not GroupPermissionAPI.can_write('custom_form'):
		return abort(403)

	# Logged in user
	if current_user and current_user.id > 0:
		user = User.query.get(current_user.id)
	else:
		# Need to be logged in
		return abort(403)

	# Test if user already signed up
	submission = CustomFormResult.query.filter(
		CustomFormResult.id == submit_id
	).first()

	if not submission:
		response = "Error, submission could not be found"

	# Adjust the "has_payed"
	if submission.has_payed:
		submission.has_payed = False
	else:
		submission.has_payed = True

	db.session.add(submission)
	db.session.commit()

	return response
