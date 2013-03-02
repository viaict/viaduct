import bcrypt

from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for
from flask import Blueprint, Markup
from flask.ext.login import current_user, login_user, logout_user

from recaptcha.client import captcha
from validate_email import validate_email

from application import application, db, login_manager
from application.user.models import User

user = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(id):
	# The hook used by the login manager to get the user from the database by
	# user ID.
	return User.query.get(int(id))

@user.route('/signup/', methods=['GET', 'POST'])
def sign_up():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	if current_user and current_user.is_authenticated():
		return redirect(url_for('index'))

	if request.method == 'POST':
		email = request.form['e-mail'].strip()
		password = request.form['password'].strip()
		repeat_password = request.form['repeat-password'].strip()
		first_name = request.form['first-name'].strip()
		last_name = request.form['last-name'].strip()
		challenge = request.form['recaptcha_challenge_field'].strip()
		response = request.form['recaptcha_response_field'].strip()
		valid_form = True

		response = captcha.submit(challenge, response,
			application.config['RECAPTCHA_PRIVATE_KEY'], request.remote_addr)

		if not email:
			flash('No e-mail address has been specified.', 'error')
			valid_form = False
		elif not validate_email(email, check_mx=True):
			flash('The e-mail address that has been specified is invalid.',
				'error')
			valid_form = False
		elif User.query.filter(User.email==email).count() > 0:
			flash('The e-mail address that has been specified is in use already.', 'error')
			valid_form = False

		if not password:
			flash('No password has been specified.', 'error')
			valid_form = False
		elif password != repeat_password:
			flash('The passwords that have been specified do not match.',
				'error')
			valid_form = False

		if not first_name:
			flash('No first name has been specified.', 'error')
			valid_form = False

		if not last_name:
			flash('No last name has been specified.', 'error')
			valid_form = False

		if not response.is_valid:
			flash('The captcha is invalid.', 'error')
			valid_form = False

		if valid_form:
			user = User(email, bcrypt.hashpw(password, bcrypt.gensalt()),
				first_name, last_name)

			db.session.add(user)
			db.session.commit()

			flash('You\'ve signed up successfully.')

			login_user(user)

			return redirect(url_for('index'))

	captcha_data = Markup(captcha.displayhtml(
		application.config['RECAPTCHA_PUBLIC_KEY'],
		use_ssl=application.config['RECAPTCHA_USE_SSL']))

	return render_template('user/sign_up.htm', captcha=captcha_data)

@user.route('/signin/', methods=['GET', 'POST'])
def sign_in():
	# Redirect the user to the index page if he or she has been authenticated
	# already.
	if current_user and current_user.is_authenticated():
		return redirect(url_for('index'))

	if request.method == 'POST':
		email = request.form['e-mail'].strip()
		password = request.form['password'].strip()
		remember_me = request.form.get('remember-me')
		valid_form = True

		# Get the user from the database if he or she exists.
		user = User.query.filter(User.email==email).first()

		# Check if the user does exist, and if the passwords do match.
		if not user or bcrypt.hashpw(password, user.password) != user.password:
			flash('The credentials that have been specified are invalid.', 'error')
			valid_form = False

		if valid_form:
			# Notify the login manager that the user has been signed in.
			login_user(user)

			flash('You\'ve been signed in successfully.')

			return redirect(url_for('index'))

	return render_template('user/sign_in.htm')

@user.route('/signout/')
def sign_out():
	# Notify the login manager that the user has been signed out.
	logout_user()

	flash('You\'ve been signed out.')

	return redirect(url_for('index'))

@user.route('/users/', methods=['GET', 'POST'])
@user.route('/users/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	# persumably, if the method is a post we have selected stuff to delete,
	# similary to groups
	if request.method == 'POST':
		used_ids = request.form.getlist('select')

		users = User.query.filter(User.id.in_(user_ids)).all()

		for user in users:
			db.session.delete(user)

		db.session.commit()

		if len(groups) > 1:
			flash('The selected users have been deleted.', 'success')
		else:
			flash('The selected user has been deleted.', 'success')

		redirect(url_for('user.view'))


	# Get a list of users to render for the current page.
	users = User.query.paginate(page, 15, False)

	return render_template('user/view.htm', users=users)

