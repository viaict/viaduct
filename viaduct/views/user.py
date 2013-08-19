import bcrypt

from flask import flash, get_flashed_messages, redirect, render_template, \
		request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user, login_user, logout_user

from viaduct import application, db, login_manager
from viaduct.helpers import flash_form_errors
from viaduct.forms import SignUpForm, SignInForm
from viaduct.models import User
from viaduct.models.group import Group
from viaduct.forms.user import CreateUserForm#, EditUserPermissionForm
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
	# TODO fix permission	
	#if not current_user.has_permission('user.create'):
	#	abort(403)
	
	return render_template('user/view_single.htm', user= User.query.get(user_id))

@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def create(user_id=None):
	if not GroupPermissionAPI.can_write('user'):
		return abort(403)

	# Select user
	if user_id:
		user = User.query.get(user_id)
	else:
		user = User()

	form = CreateUserForm(request.form)

	# Add education.
	educations = Education.query.all()
	form.education_id.choices = \
			[(e.id, e.name) for e in educations]

	if form.validate_on_submit():
		if User.query.filter(User.email == form.email.data).count() > 0:
			flash('Een gebruiker met dit email adres bestaat al / A user with the e-mail address specified does already exist.', 'error')
			return render_template('user/create_user.htm', form=form)

		user = User(form.email.data, bcrypt.hashpw(form.password.data,
				bcrypt.gensalt()), form.first_name.data, form.last_name.data,
				form.student_id.data, form.education_id.data)
		db.session.add(user)

		group = Group.query.filter(Group.name=='all').first()
		group.add_user(user)

		db.session.add(group)
		db.session.commit()

		#user.add_to_all()

		try:
			db.session.commit()
		except Exception as exception:
			db.session.flush()
			flash('An error occured with the database while creating the user.', 'error')
			return render_template('user/create_user.htm', form=form)

		flash('The user has been created successfully.', 'success')
		return redirect(url_for('user.view'))
	else:
		flash_form_errors(form)

	return render_template('user/create_user.htm', form=form)

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
@blueprint.route('/users/<int:page_id>/', methods=['GET', 'POST'])
def view(page_id=1):
	#if not current_user.has_permission('user.view'):
	#	abort(403)

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
	users = User.query.paginate(page_id, 15, False)

	return render_template('user/view.htm', users=users)

#@blueprint.route('/users/edit-permissions/<int:user_id>/', methods=['GET', 'POST'])
#@blueprint.route('/users/edit-permissions/<int:user_id>/<int:page_id>/', methods=['GET', 'POST'])
#def edit_permissions(user_id, page_id=1):
#	if not GroupPermissionAPI.can_write('user'):
#		return abort(403)
#
#	user = User.query.filter(User.id==user_id).first()
#	form = EditUserPermissionForm()
#	pagination = Permission.query.paginate(page_id, 15, False)
#
#	if form.validate_on_submit():
#		for form_entry, permission in zip(form.permissions, pagination.items):
#			if form_entry.select.data > 0:
#				user.add_permission(permission.name, True)
#			elif form_entry.select.data < 0:
#				user.add_permission(permission.name, False)
#			else:
#				user.delete_permission(permission.name)
#
#		return redirect(url_for('user.view'))
#	else:
#		for permission in pagination.items:
#			form.permissions.append_entry({'select': user.get_permission(permission.name)})
#
#	return render_template('user/edit_permissions.htm', form=form,
#			pagination=pagination,
#			permissions=zip(pagination.items, form.permissions))

