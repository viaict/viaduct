from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

vacancy = Blueprint('vacancy', __name__)

@vacancy.route('/vacancies/', methods=['GET', 'POST'])
@vacancy.route('/vacancies/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	vacancies = vacancy.query.paginate(page, 15, False)

	return render_template('vacancy/view.htm', vacancies=vacancies)

@vacancy.route('/vacancies/create/', methods=['GET', 'POST'])
def create():
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if request.method == 'POST':
		title = request.form['title'].strip()
		description = request.form['description'].strip()
		
		valid_form = True

		if valid_form:
			vacancy = Vacancy(title, description)

			db.session.add(vacancy)
			db.session.commit()

			flash('The vacancy has been added.', 'success')

			return redirect(url_for('vacancy.view'))

	return render_template('vacancy/create.htm')