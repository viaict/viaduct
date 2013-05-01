import os

from flask import flash, get_flashed_messages, redirect, render_template, \
	request, url_for, abort
from flask import Blueprint, Markup
from flask.ext.login import current_user

from werkzeug import secure_filename

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from forms import CreateForm
from models import Activity

#from dateutil.parser import parse
import datetime

blueprint = Blueprint('activity', __name__)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'gif', 'jpeg'])

# Overview of activities
@blueprint.route('/activities/', methods=['GET', 'POST'])
@blueprint.route('/activities/<int:page>/', methods=['GET', 'POST'])
def view(page=1):
	activities = Activity.query \
		.order_by(Activity.start_time.desc()) \
		.paginate(page, 15, False)

	return render_template('activity/view.htm', activities=activities)

@blueprint.route('/activity/<int:activity_id>', methods=['GET', 'POST'])
def get_activity(activity_id = 0):
	activity = Activity.query.filter(Activity.id == activity_id).first()
	return render_template('activity/view_single.htm', activity=activity)

@blueprint.route('/activity/create/', methods=['GET', 'POST'])
@blueprint.route('/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
def create(activity_id=None):
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if activity_id:
		activity = Activity.query.filter(Activity.id == activity_id).first()
	else:
		activity = None

	form = CreateForm(request.form, activity)

	if request.method == 'POST':
		valid_form = True

		owner_id		= current_user.id
		name				= form.name.data
		description	= request.form['description'].strip()

		start_date = request.form['start_date'].strip()
		start_time = request.form['start_time'].strip()

		start = datetime.datetime.strptime(start_date + start_time, '%Y-%m-%d%H:%M')

		end_date = request.form['end_date'].strip()
		end_time = request.form['end_time'].strip()

		end = datetime.datetime.strptime(end_date + end_time, '%Y-%m-%d%H:%M')

		location		= request.form['location'].strip()
		privacy			= "public"
		price				= request.form['price'].strip()

		file = request.files['picture']

		if file and allowed_file(file.filename):
			picture = secure_filename(file.filename)
			file.save(os.path.join('viaduct/static/activity_pictures', picture))
		else:
			picture = "yolo.png"
	
		venue	= 1 # Facebook ID location, not used yet

		if not name:
			flash('No activity name has been specified.', 'error')
			valid_form = False

		if not description:
			flash('The activity requires a description.', 'error')
			valid_form = False

		if valid_form:
			activity = Activity(
				owner_id,
				name, 
				description, 
				start, 
				end, 
				location, 
				privacy,
				price,
				picture,
				venue
			)
			
			db.session.add(activity)
			db.session.commit()

			flash('You\'ve created an activity successfully.')

			return redirect(url_for('activity.view'))
	else:
		flash_form_errors(form)

	return render_template('activity/create.htm', form=form)
