import bcrypt

from flask import flash, get_flashed_messages, redirect, render_template, \
		request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user, login_user, logout_user

from viaduct import application, db, login_manager
from viaduct.helpers import flash_form_errors
from viaduct.forms import SignUpForm, SignUpFormNoCaptcha, SignInForm
from viaduct.models import User, UserPermission

blueprint = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(id):
	# The hook used by the login manager to get the user from the database by
	# user ID.
	return User.query.get(int(id))

@blueprint.route('/users/create', methods=['GET', 'POST'])
def create_user():
	if not current_user.has_permission('user.create'):
		abort(403)

	form = SignUpFormNoCaptcha(request.form)

	if form.validate_on_submit():

		email_unique = True
		for user_it in User.query.all():
			if form.email.data == user_it.email:
				email_unique = False
				break

		if email_unique:
			user = User(form.email.data, bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
			form.first_name.data, form.last_name.data, form.student_id.data)

			db.session.add(user)
			db.session.commit()

			flash('User successfully created.')
			return redirect(url_for('user.create_user'))
		else:
			flash("Email already exists in database.");

	else:
		flash_form_errors(form)

	return render_template('user/create_user.htm', form=form)


@blueprint.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	if current_user and current_user.is_authenticated():
		return redirect(url_for('page2.get_page'))

	form = SignUpForm(request.form)

	if form.validate_on_submit():
		user = User(form.email.data, bcrypt.hashpw(form.password.data, bcrypt.gensalt()),
			form.first_name.data, form.last_name.data, form.student_id.data)

		db.session.add(user)
		db.session.commit()

		flash('You\'ve signed up successfully.')

		login_user(user)

		return redirect(url_for('page2.get_page'))
	else:
		flash_form_errors(form)

	return render_template('user/sign_up.htm', form=form)

@blueprint.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	if current_user and current_user.is_authenticated():
		return redirect(url_for('page2.get_page'))

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

			# return redirect(url_for('page.get_page'))
			return redirect('/')
	else:
		flash_form_errors(form)

	return render_template('user/sign_in.htm', form=form)

@blueprint.route('/sign-out/')
def sign_out():
	# Notify the login manager that the user has been signed out.
	logout_user()

	flash('You\'ve been signed out.')

	# FIX THIS!
	# return redirect(url_for('page.get_page'))
	return redirect('/')

@blueprint.route('/users/', methods=['GET', 'POST'])
@blueprint.route('/users/<int:page>/', methods=['GET', 'POST'])
def view(page=1):
	if not current_user.has_permission('user.view'):
		abort(403)

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
	users = User.query.paginate(page, 15, False)

	return render_template('user/view.htm', users=users)

