import bcrypt

from flask import flash, get_flashed_messages, redirect, render_template, \
		request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user, login_user, logout_user

from sqlalchemy import or_

from viaduct import application, db, login_manager
from viaduct.helpers import flash_form_errors
from viaduct.forms import SignUpForm, SignInForm
from viaduct.models import User
from viaduct.models.group import Group
from viaduct.forms.user import EditUserForm, EditUserInfoForm#, EditUserPermissionForm
from viaduct.models.education import Education
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(user_id):
	# The hook used by the login manager to get the user from the database by
	# user ID.
	user = User.query.get(int(user_id))

	return user

@blueprint.route('/users/view/<int:user_id>', methods=['GET'])
def view_single(user_id=None):
	if not GroupPermissionAPI.can_read('user') and (current_user == None or current_user.id != user_id):
		return abort(403)
	return render_template('user/view_single.htm', user= User.query.get(user_id))

@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id=None):
	if not GroupPermissionAPI.can_write('user') and (current_user == None or current_user.id != user_id):
		return abort(403)

	# Select user
	if user_id:
		user = User.query.get(user_id)
	else:
		user = User()

	if GroupPermissionAPI.can_write('user'):
		form = EditUserForm(request.form, user)
		isAdmin = True
	else:
		form = EditUserInfoForm(request.form, user)
		isAdmin = False

	# Add education.
	educations = Education.query.all()
	form.education_id.choices = [(e.id, e.name) for e in educations]

	if form.validate_on_submit():

		# Only new users need a unique email.
		query = User.query.filter(User.email == form.email.data)
		if user_id: query = query.filter(User.id != user_id)

		if query.count() > 0:
			flash('Een gebruiker met dit email adres bestaat al / A user with the e-mail address specified does already exist.', 'error')
			return render_template('user/edit.htm', form=form, user=user)

		# Because the user model is constructed to have an ID of 0 when it is
		# initialized without an email adress provided, reinitialize the user
		# with a default string for email adress, so that it will get a unique
		# ID when committed to the database.
		if not user_id:
			user = User('_')

		user.email = form.email.data
		user.first_name = form.first_name.data
		user.last_name = form.last_name.data
		if GroupPermissionAPI.can_write('user'):
			user.has_payed = form.has_payed.data
		user.student_id = form.student_id.data
		user.education_id = form.education_id.data

		if not user_id:
			user.password = bcrypt.hashpw(form.password.data, bcrypt.gensalt())

		db.session.add(user)

		group = Group.query.filter(Group.name=='all').first()
		group.add_user(user)

		db.session.add(group)
		db.session.commit()

		flash('The user has been %s successfully.' %
			('edited' if user_id else 'created'), 'success')

		if not user_id:
			return redirect(url_for('user.view'))
	else:
		flash_form_errors(form)

	return render_template('user/edit.htm', form=form, user=user, isAdmin=isAdmin)

@blueprint.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	if current_user and current_user.is_authenticated():
		return redirect(url_for('page.get_page'))

	form = SignUpForm(request.form)

	# Add education.
	educations = Education.query.all()
	form.education_id.choices = \
			[(e.id, e.name) for e in educations]

	if form.validate_on_submit():
		user = User(form.email.data, bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
			form.first_name.data, form.last_name.data, form.student_id.data, form.education_id.data)

		exists = User.query.filter(User.email==user.email)

		if exists:

			db.session.add(user)
			db.session.commit()

			group = Group.query.filter(Group.name=='all').first()
			group.add_user(user)

			db.session.add(group)
			db.session.commit()
			#user.add_to_all()

			flash('You\'ve signed up successfully.')

		login_user(user)

		return redirect(url_for('page.get_page'))
	else:
		flash_form_errors(form)

	return render_template('user/sign_up.htm', form=form)

@blueprint.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	#if current_user and current_user.is_authenticated():
	#	return redirect(url_for('page.get_page'))

	form = SignInForm(request.form)

	if form.validate_on_submit():
		valid_form = True

		user = User.query.filter(User.email==form.email.data).first()

		# Check if the user does exist, and if the passwords do match.
		if not user or bcrypt.hashpw(form.password.data, user.password) != user.password:
			flash('The credentials that have been specified are invalid.', 'error')
			valid_form = False

		if valid_form:
			# Notify the login manager that the user has been signed in.
			login_user(user)

			flash('You\'ve been signed in successfully.')

			return redirect(url_for('page.get_page'))
	else:
		flash_form_errors(form)

	return render_template('user/sign_in.htm', form=form)

@blueprint.route('/sign-out/')
def sign_out():
	# Notify the login manager that the user has been signed out.
	logout_user()

	flash('You\'ve been signed out.')

	return redirect(url_for('page.get_page'))

@blueprint.route('/users/', methods=['GET', 'POST'])
@blueprint.route('/users/<int:page_nr>/', methods=['GET', 'POST'])
def view(page_nr=1):
	#if not current_user.has_permission('user.view'):
	#	abort(403)
	if not GroupPermissionAPI.can_read('user'):
		return abort(403)

	if request.args.get('search') != None:
		search = request.args.get('search')
		users = User.query.\
			filter(or_(User.first_name.like('%' + search + '%'),
				User.last_name.like('%' + search + '%'),
				User.email.like('%' + search + '%'),
				User.student_id.like('%' + search + '%'))).order_by(User.first_name).order_by(User.last_name).paginate(page_nr, 15, False)
		return render_template('user/view.htm', users=users, search=search)

	# persumably, if the method is a post we have selected stuff to delete,
	# similary to groups
	if request.method == 'POST':
		user_ids = request.form.getlist('select')

		users = User.query.filter(User.id.in_(user_ids)).all()

		for user in users:
			db.session.delete(user)

		db.session.commit()

		if len(users) > 1:
			flash('The selected users have been deleted.', 'success')
		else:
			flash('The selected user has been deleted.', 'success')

		redirect(url_for('user.view'))

	# Get a list of users to render for the current page.
	users = User.query.order_by(User.first_name).order_by(User.last_name)\
				.paginate(page_nr, 15, False)

	return render_template('user/view.htm', users=users)
