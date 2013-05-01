from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

contact_information = Blueprint('contact_information', __name__)

@contact_information.route('/contact_information/', methods=['GET', 'POST'])
@contact_information.route('/contact_information/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	contact_information = contact_information.query.paginate(page, 15, False)

	return render_template('contact_information/view.htm', contact_information=contact_information)

@contact_information.route('/contact_information/create/', methods=['GET', 'POST'])
def create():
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if request.method == 'POST':
		name = request.form['name'].strip()
		email = request.form['e-mail'].strip() # FUCKING RETARDED KUT STREEPJE
		phone_nr = request.form['phone_nr'].strip()
		location_id = request.form['location_id']
		
		valid_form = True

		if valid_form:
			contact_information = Contact_information(name, email, phone_nr, location_id)

			db.session.add(contact_information)
			db.session.commit()

			flash('The contact_information has been added.', 'success')

			return redirect(url_for('contact_information.view'))

	return render_template('contact_information/create.htm')