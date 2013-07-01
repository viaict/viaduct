from flask import Blueprint, render_template

from viaduct import application, db
from viaduct.models.vacancy import Vacancy

blueprint = Blueprint('vacancy', __name__)

@blueprint.route('/vacancies/', methods=['GET', 'POST'])
@blueprint.route('/vacancies/<int:page>/', methods=['GET', 'POST'])
def view(page=1):
	vacancies = Vacancy.query.paginate(page, 15, False)

	return render_template('vacancy/view.htm', vacancies=vacancies)

@blueprint.route('/vacancies/create/', methods=['GET', 'POST'])
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