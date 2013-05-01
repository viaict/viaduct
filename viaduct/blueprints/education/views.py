from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

education = Blueprint('education', __name__)

@education.route('/education/', methods=['GET', 'POST'])
@education.route('/education/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	education = education.query.paginate(page, 15, False)

	return render_template('education/view.htm', education=education)

@education.route('/education/create/', methods=['GET', 'POST'])
def create():
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if request.method == 'POST':
		title = request.form['title'].strip()
		description = request.form['description'].strip()
		type = request.form['type']
		
		valid_form = True

		if valid_form:
			education = education(title, description, type)

			db.session.add(education)
			db.session.commit()

			flash('The education has been added.', 'success')

			return redirect(url_for('education.view'))

	return render_template('education/create.htm')