import os, datetime

from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user

from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.forms.activity import CreateForm
from viaduct.models.activity import Activity
from viaduct.models.custom_form import CustomForm, CustomFormResult

blueprint = Blueprint('activity', __name__)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'gif', 'jpeg'])

# Overview of activities
@blueprint.route('/activities/', methods=['GET', 'POST'])
@blueprint.route('/activities/<string:archive>/', methods=['GET', 'POST'])
@blueprint.route('/activities/page/<int:page>', methods=['GET', 'POST'])
@blueprint.route('/activities/<string:archive>/page/<int:page>', methods=['GET', 'POST'])
def view(archive="", page=1):

	if archive == "archive":
		activities = Activity.query \
			.filter(Activity.end_time < datetime.datetime.today()) \
			.order_by(Activity.start_time.desc())
	else :
		activities = Activity.query \
			.filter(Activity.end_time > (datetime.datetime.now() - datetime.timedelta(hours=12))) \
			.order_by(Activity.start_time.asc())

	return render_template('activity/view.htm', activities=activities.paginate(page, 10, False), archive=archive)

@blueprint.route('/activities/<int:activity_id>', methods=['GET', 'POST'])
def get_activity(activity_id = 0):
	activity = Activity.query.get(activity_id)

	if not activity:
		return abort(404)

	if activity.form_id:
		activity.form = CustomForm.query.get(activity.form_id)

		form_result = CustomFormResult.query \
			.filter(CustomFormResult.form_id  == activity.form_id) \
			.filter(CustomFormResult.owner_id == current_user.id).first()

		activity.form_data = form_result.data.replace('"', "'")

	return render_template('activity/view_single.htm', activity=activity)

@blueprint.route('/activities/create/', methods=['GET', 'POST'])
@blueprint.route('/activities/edit/<int:activity_id>', methods=['GET', 'POST'])
def create(activity_id=None):
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if activity_id:
		activity = Activity.query.filter(Activity.id == activity_id).first()

		if not activity:
			abort(404)
	else:
		activity = Activity()

	form = CreateForm(request.form, activity)

	# Add companies.
	form.form_id.choices = \
		[(c.id, c.name) for c in CustomForm.query.order_by('name')]

	# Set default to "No form"
	form.form_id.choices.insert(0, (0, 'Geen formulier'))

	if request.method == 'POST':
		valid_form = True

		owner_id		= current_user.id

		name				= form.name.data
		description	= form.description.data

		start_date = form.start_date.data
		start_time = form.start_time.data
		
		end_date = form.end_date.data
		end_time = form.end_time.data

		start = datetime.datetime.strptime(start_date + start_time, '%Y-%m-%d%H:%M')
		end = datetime.datetime.strptime(end_date + end_time, '%Y-%m-%d%H:%M')

		location = form.location.data
		price	= form.price.data

		file = request.files['picture']

		if file and allowed_file(file.filename):
			picture = secure_filename(file.filename)
			file.save(os.path.join('viaduct/static/activity_pictures', picture))

			# Remove old picture
			if activity.picture:
				os.remove(os.path.join('viaduct/static/activity_pictures', activity.picture))

		elif activity.picture:
			picture = activity.picture
		else:
			picture = None

		venue	= 1 # Facebook ID location, not used yet

		if form.form_id and form.form_id.data > 0:
			activity.form_id = form.form_id.data

		if valid_form:
			activity.name = name 
			activity.description = description
			activity.start_time = start
			activity.end_time = end 
			activity.location = location
			activity.price = price
			activity.picture = picture

			if activity.id:
				flash('You\'ve created an activity successfully.', 'success')
			else:
				flash('You\'ve updated an activity successfully.', 'success')

			db.session.add(activity)
			db.session.commit()

			return redirect(url_for('activity.view'))
	else:
		flash_form_errors(form)

	return render_template('activity/create.htm', form=form)

