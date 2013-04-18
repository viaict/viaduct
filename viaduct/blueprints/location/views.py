from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

location = Blueprint('location', __name__)

@location.route('/location/', methods=['GET', 'POST'])
@location.route('/location/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	location = location.query.paginate(page, 15, False)

	return render_template('location/view.htm', location=location)

@location.route('/location/create/', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		email = request.form['email'].strip()
		phone_nr = request.form['phone_nr'].strip()
		city = request.form['city'].strip()
		street = request.form['street'].strip()
		street_nr = request.form['street_nr'].strip()
		zip = request.form['zip'].strip()
		postoffice_box = request.form['postoffice_box'].strip()
		
		valid_form = True

		if valid_form:
			location = Location(email, phone_nr, city, street, street_nr, zip, postoffice_box)

			db.session.add(location)
			db.session.commit()

			flash('The location has been added.', 'success')

			return redirect(url_for('location.view'))

	return render_template('location/create.htm')