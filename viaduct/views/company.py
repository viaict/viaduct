from flask import Blueprint, flash, redirect, render_template, request, url_for

from viaduct import db
from viaduct.models.company import Company
from viaduct.models.location import Location
from viaduct.models.contact import Contact
from viaduct.forms import CompanyForm

blueprint = Blueprint('company', __name__)

@blueprint.route('/companies/', methods=['GET', 'POST'])
@blueprint.route('/companies/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
	companies = Company.query.paginate(page, 15, False)

	return render_template('company/list.htm', companies=companies)

@blueprint.route('/companies/create/', methods=['GET'])
@blueprint.route('/companies/edit/<int:company_id>/', methods=['GET'])
def view(company_id=None):
	''' FRONTEND
	Create, view or edit a company. '''

	# Select company.
	if company_id:
		company = Company.query.get(company_id)
	else:
		company = Company()

	form = CompanyForm(request.form, company)

	# Add locations.
	locations = Location.query.order_by('address').order_by('city')
	form.location_id.choices = \
			[(l.id, l.address + ', ' + l.city) for l in locations]

	# Add contacts.
	form.contact_id.choices = \
			[(c.id, c.name) for c in Contact.query\
					.filter_by(location=locations.first()).order_by('name')]

	return render_template('company/view.htm', company=company, form=form)

@blueprint.route('/companies/create/', methods=['POST'])
@blueprint.route('/companies/edit/<int:company_id>/', methods=['POST'])
def update(company_id=None):
	''' BACKEND
	Create, view or edit a company. '''

	# Select company.
	if company_id:
		company = Company.query.get(company_id)
	else:
		company = Company()

	form = CompanyForm(request.form, company)

	# Add locations.
	locations = Location.query.order_by('address').order_by('city')
	form.location_id.choices = \
			[(l.id, l.address + ', ' + l.city) for l in locations]

	# Add contacts.
	form.contact_id.choices = \
			[(c.id, c.name) for c in Contact.query.order_by('name')]

	if form.validate_on_submit():
		company.name = form.name.data
		company.description = form.description.data
		company.contract_start_date = form.contract_start_date.data
		company.contract_end_date = form.contract_end_date.data
		company.location = Location.query.get(form.location_id.data)
		company.contact = Contact.query.get(form.contact_id.data)

		db.session.add(company)
		db.session.commit()

		if company_id:
			flash('Bedrijf opgeslagen', 'success')
		else:
			company_id = company.id
			flash('Bedrijf aangemaakt', 'success')
	else:
		error_handled = False
		if not form.title.data:
			flash('Geen titel opgegeven', 'error')
			error_handled = True
		if not form.description.data:
			flash('Geen beschrijving opgegeven', 'error')
			error_handled = True
		if not form.contract_start_date.data:
			flash('Geen contract begindatum opgegeven', 'error')
			error_handled = True
		if not form.contract_end_date.data:
			flash('Geen contract einddatum opgegeven', 'error')
			error_handled = True

		if not error_handled:
			flash_form_errors(form)

	return redirect(url_for('company.view', company_id=company_id))

@blueprint.route('/companies/delete/<int:company_id>/', methods=['POST'])
def delete(company_id):
	''' BACKEND
	Delete a company. '''

	company = Company.query.get(company_id)
	if not company:
		return abort(404)

	db.session.delete(company)
	db.session.commit()
	flash('Bedrijf verwijderd', 'success')

	return redirect(url_for('company.list'))