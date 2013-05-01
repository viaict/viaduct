from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from forms import CreateForm
from models import Activity

blueprint = Blueprint('activity', __name__)

# Overview of activities
@blueprint.route('/activities/', methods=['GET', 'POST'])
@blueprint.route('/activities/<int:page>/', methods=['GET', 'POST'])
def view(page=1):
	activities = Activity.query.paginate(page, 15, False)

	return render_template('activity/view.htm', activities=activities)

@blueprint.route('/activity/create/', methods=['GET', 'POST'])
def create():
	form = CreateForm(request.form)

	if request.method == 'POST':
		valid_form = True

		title = request.form['title'].strip()
		description = request.form['description'].strip()

		if not title:
			flash('No activity title has been specified.', 'error')
			valid_form = False

		if valid_form:
			activity = Activity(
				title,
				description
			)
			
			db.session.add(activity)
			db.session.commit()

			flash('You\'ve created an activity successfully.')

			return redirect(url_for('page.get_page'))
	else:
		flash_form_errors(form)

	return render_template('activity/create.htm', form=form)
