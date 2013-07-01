from flask import Blueprint, render_template, request, redirect, url_for,\
		abort, flash

from viaduct import application, db
from viaduct.models.vacancy import Vacancy
from viaduct.models.company import Company
from viaduct.forms import VacancyForm

blueprint = Blueprint('vacancy', __name__)

@blueprint.route('/vacancies/', methods=['GET', 'POST'])
@blueprint.route('/vacancies/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
	vacancies = Vacancy.query.paginate(page, 15, False)

	return render_template('vacancy/list.htm', vacancies=vacancies)

@blueprint.route('/vacancies/create/', methods=['GET'])
@blueprint.route('/vacancies/edit/<int:vacancy_id>/', methods=['GET'])
def view(vacancy_id=None):
	''' FRONTEND
	Create, view or edit a vacancy. '''

	# Select vacancy.
	if vacancy_id:
		vacancy = Vacancy.query.get(vacancy_id)
	else:
		vacancy = Vacancy()

	form = VacancyForm(request.form, vacancy)

	# Add companies.
	form.company_id.choices = \
			[(c.id, c.name) for c in Company.query.order_by('name')]

	return render_template('vacancy/view.htm', vacancy=vacancy, form=form)

@blueprint.route('/vacancies/create/', methods=['POST'])
@blueprint.route('/vacancies/edit/<int:vacancy_id>/', methods=['POST'])
def update(vacancy_id=None):
	''' BACKEND
	Create, view or edit a vacancy. '''

	# Select vacancy.
	if vacancy_id:
		vacancy = Vacancy.query.get(vacancy_id)
	else:
		vacancy = Vacancy()

	form = VacancyForm(request.form, vacancy)

	# Add companies.
	form.company_id.choices = \
			[(c.id, c.name) for c in Company.query.order_by('name')]

	if form.validate_on_submit():
		vacancy.title = form.title.data
		vacancy.description = form.description.data
		vacancy.start_date = form.start_date.data
		vacancy.end_date = form.end_date.data
		vacancy.contract_of_service = form.contract_of_service.data
		vacancy.workload = form.workload.data
		vacancy.company = Company.query.get(form.company_id.data)

		db.session.add(vacancy)
		db.session.commit()

		if vacancy_id:
			flash('Vacature opgeslagen', 'success')
		else:
			vacancy_id = vacancy.id
			flash('Vacature aangemaakt', 'success')
	else:
		error_handled = False
		if not form.title.data:
			flash('Geen titel opgegeven', 'error')
			error_handled = True
		if not form.description:
			flash('Geen beschrijving opgegeven', 'error')
			error_handled = True
		if not form.start_date:
			flash('Geen begindatum opgegeven', 'error')
			error_handled = True
		if not form.end_date:
			flash('Geen einddatum opgegeven', 'error')
			error_handled = True
		if not form.workload:
			flash('Geen werklast opgegeven', 'error')
			error_handled = True

		if not error_handled:
			flash_form_errors(form)

	return redirect(url_for('vacancy.view', vacancy_id=vacancy_id))

@blueprint.route('/vacancies/delete/<int:vacancy_id>/', methods=['POST'])
def delete(vacancy_id):
	''' BACKEND
	Delete a vacancy. '''

	vacancy = Vacancy.query.get(vacancy_id)
	if not vacancy:
		return abort(404)

	db.session.delete(vacancy)
	db.session.commit()
	flash('Vacature verwijderd', 'success')

	return redirect(url_for('vacancy.list'))