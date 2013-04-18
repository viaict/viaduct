from flask import Blueprint, flash, redirect, render_template, request, url_for

from application import db

study = Blueprint('study', __name__)

@study.route('/studies/', methods=['GET', 'POST'])
@study.route('/studies/<int:page>/', methods=['GET', 'POST'])
def view(page=1):

	studies = Study.query.paginate(page, 15, False)

	return render_template('study/view.htm', studies=studies)

@study.route('/studies/create/', methods=['GET', 'POST'])
def create():
	if request.method == 'POST':
		title = request.form['title'].strip()
		description = request.form['description'].strip()
		type = request.form['type']
		
		valid_form = True

		if valid_form:
			study = Study(title, description, type)

			db.session.add(study)
			db.session.commit()

			flash('The study has been added.', 'success')

			return redirect(url_for('study.view'))

	return render_template('study/create.htm')