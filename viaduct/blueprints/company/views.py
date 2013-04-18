from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

company = Blueprint('company', __name__)

@company.route('/companies/', methods=['GET', 'POST'])
@company.route('/companies/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	companies = company.query.paginate(page, 15, False)

	return render_template('company/view.htm', companies=companies)

@company.route('/companies/create/', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		title = request.form['title'].strip()
		description = request.form['description'].strip()
		contract_start_date = request.form['contract_start_date']
		contract_end_date = request.form['contract_end_date']
		headquarter_location_id = request.form['location_id']
		contact_id = request.form['contact_id']
		
		valid_form = True

		if valid_form:
			company = Company(title, description, contact_start_date, contact_end_date, headquarter_location_id, contact_id)

			db.session.add(company)
			db.session.commit()

			flash('The company has been added.', 'success')

			return redirect(url_for('company.view'))

	return render_template('company/create.htm')