from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from models import Activity

blueprint = Blueprint('activity', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<path:path>', methods=['GET', 'POST'])

# Overview of activities
def view(page=1):
	users = Activity.query.paginate(page, 15, False)

	return render_template('activity/view.htm', activities=activity)

@blueprint.route('/sign-up/', methods=['GET', 'POST'])
def create():
	form = CreateForm(request.form)

	if form.validate_on_submit():
		activity = Activity(
			form.title.data, 
			form.description.data
		)
		
		db.session.add(activity)
		db.session.commit()

		flash('You\'ve created an activity successfully.')

		#return redirect(url_for('page.get_page'))
	else:
		flash_form_errors(form)

	return render_template('activity/create.htm', form=form)
