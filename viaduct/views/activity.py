import os
import datetime

# this is now uncommented for breaking activity for some reason
# please some one check out what is happening
import viaduct.api.google as google

from flask import flash, redirect, render_template, request, url_for, abort,\
    jsonify
from flask import Blueprint
from flask.ext.login import current_user
from flask.ext.babel import _  # gettext

from werkzeug import secure_filename

from viaduct import db
from viaduct.helpers import flash_form_errors, get_login_form
from viaduct.forms.activity import ActivityForm, CreateForm
from viaduct.models.activity import Activity
from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct.models.mollie import Transaction
from viaduct.api.module import ModuleAPI
from viaduct.api.mollie import MollieAPI
from viaduct.models.education import Education

from viaduct.utilities.serialize_sqla import serialize_sqla

blueprint = Blueprint('activity', __name__, url_prefix='/activities')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in \
        set(['png', 'jpg', 'gif', 'jpeg'])


# Overview of activities
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<string:archive>/', methods=['GET', 'POST'])
@blueprint.route('/list/<int:page_nr>/', methods=['GET', 'POST'])
@blueprint.route('/list/<string:archive>/<int:page_nr>/',
                 methods=['GET', 'POST'])
def view(archive=None, page_nr=1):
    if not ModuleAPI.can_read('activity'):
        return abort(403)

    if archive == "archive":
        activities = Activity.query.filter(
            Activity.end_time < datetime.datetime.today()).order_by(
                Activity.start_time.desc())
        title = _('Activity archive') + " - " + _('page') + " " + str(page_nr)
    else:
        activities = Activity.query.filter(
            Activity.end_time > (
                datetime.datetime.now() - datetime.timedelta(hours=12))) \
            .order_by(Activity.start_time.asc())
        title = _('Activities') + ' - ' + _('page') + ' ' + str(page_nr)

    return render_template('activity/view.htm',
                           activities=activities.paginate(page_nr, 10, False),
                           archive=archive, title=title)


@blueprint.route('/remove/<int:activity_id>/', methods=['POST'])
def remove_activity(activity_id=0):
    if not ModuleAPI.can_write('activity'):
        return abort(403)

    # Get activity
    activity = Activity.query.filter(Activity.id == activity_id).first()

    # Remove the event from google calendar
    google.delete_activity(activity.google_event_id)

    # Remove it
    db.session.delete(activity)
    db.session.commit()

    return redirect(url_for('activity.view'))


@blueprint.route('/<int:activity_id>/', methods=['GET', 'POST'])
def get_activity(activity_id=0):
    if not ModuleAPI.can_read('activity'):
        return abort(403)

    activity = Activity.query.get(activity_id)

    if not activity:
        return abort(404)

    form = ActivityForm(request.form, current_user)

    # Add education for activity form
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    # Check if there is a custom_form for this activity
    if activity.form_id:
        # Add the form
        activity.form = CustomForm.query.get(activity.form_id)

        # Count current attendants for "reserved" message
        entries = CustomFormResult.query.filter(CustomFormResult.form_id ==
                                                activity.form_id)
        activity.num_attendants = entries.count()

        # Check if the current user has already entered data in this custom
        # form
        if current_user and current_user.id > 0:
            form_result = CustomFormResult.query \
                .filter(CustomFormResult.form_id == activity.form_id) \
                .filter(CustomFormResult.owner_id == current_user.id).first()

            if form_result:
                activity.form_data = form_result.data.replace('"', "'")
                if not form_result.has_payed:
                    # There is 50 cents administration fee
                    if form_result.form.price - 0.5 > 0:
                        activity.form.show_pay_button = True
                        activity.form.id = form_result.id

                if form_result.has_payed:
                    activity.info = _("Your registration has been completed")\
                        + _("You can edit your registration by resubmitting"
                            "the form.")
                else:
                    activity.info = _("You have successfully registered"
                                      ", payment is still required!")
            else:
                if activity.num_attendants >= activity.form.max_attendants:
                    activity.info = _("The activity has reached its maximum "
                                      "number of registrations. You have been "
                                      "placed on the reserves list.")
                else:
                    activity.info = _("The number of registrations at this "
                                      "moment is") + ": " +\
                        str(activity.num_attendants)

    return render_template('activity/view_single.htm', activity=activity,
                           form=form, login_form=get_login_form(),
                           title=activity.name)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:activity_id>/', methods=['GET', 'POST'])
def create(activity_id=None):
    # Need to be logged in + actie group or admin etc.
    if not ModuleAPI.can_write('activity'):
        return abort(403)

    if activity_id:
        activity = Activity.query.get(activity_id)

        if not activity:
            abort(404)

        title = _("Edit") + " " + str(activity.name)
    else:
        activity = Activity()
        title = _('Create activity')

    form = CreateForm(request.form, activity)

    # Add a dropdown select for available custom_forms
    form.form_id.choices = \
        [(c.id, c.name) for c in CustomForm.query.order_by('name')]

    # Set default to "No form"
    form.form_id.choices.insert(0, (0, _('No form')))

    if request.method == 'POST':
        if form.validate_on_submit():

            form.populate_obj(activity)

            file = request.files['picture']

            if file and allowed_file(file.filename):
                picture = secure_filename(file.filename)
                file.save(os.path.join('viaduct/static/activity_pictures',
                                       picture))

                # Remove old picture
                if activity.picture:
                    try:
                        os.remove(os.path.join(
                            'viaduct/static/activity_pictures',
                            activity.picture))
                    except OSError:
                        print(_('Cannot delete image, image does not exist') +
                              ": " + str(activity.picture))

            elif activity.picture:
                picture = activity.picture
            else:
                picture = None

            venue = 1  # Facebook ID location, not used yet  # noqa

            # Set a custom_form if it actually exists
            if form.form_id and form.form_id.data > 0:
                activity.form_id = form.form_id.data
            else:
                activity.form_id = None

            activity.picture = picture
            activity.owner_id = current_user.id

            if activity.id and activity.google_event_id:
                flash(_('The activity has been edited.'), 'success')

                google.update_activity(activity.google_event_id,
                                       form.nl_name.data,
                                       form.nl_description.data,
                                       form.location.data,
                                       form.start_time.data.isoformat(),
                                       form.end_time.data.isoformat())
            else:
                flash(_('The activity has been created.'), 'success')

                google_activity = google.insert_activity(
                    form.nl_name.data, form.nl_description.data,
                    form.location.data, form.start_time.data.isoformat(),
                    form.end_time.data.isoformat())

                if google_activity:
                    activity.google_event_id = google_activity['id']

            db.session.add(activity)
            db.session.commit()

            return redirect(url_for('activity.get_activity',
                                    activity_id=activity.id))
        else:
            flash_form_errors(form)

    return render_template('activity/create.htm', activity=activity, form=form,
                           title=title)


@blueprint.route('/transaction/<int:result_id>/', methods=['GET', 'POST'])
def create_mollie_transaction(result_id):
    form_result = CustomFormResult.query.filter(
        CustomFormResult.id == result_id).first()
    transaction = Transaction.query\
        .filter(Transaction.form_result_id == form_result.id)\
        .filter(Transaction.status == 'open').first()
    if not transaction or not transaction.mollie_id:
        description = form_result.form.transaction_description
        description = "VIA transaction: " + description
        print(description)
        amount = form_result.form.price
        user = form_result.owner
        payment_url, transaction = MollieAPI.create_transaction(
            amount, description, user=user, form_result=form_result)
        if payment_url:
            return redirect(payment_url)
        else:
            return render_template('mollie/success.htm', message=transaction)
    else:
        payment_url, message = MollieAPI.get_payment_url(
            mollie_id=transaction.mollie_id)
        if payment_url:
            return redirect(payment_url)
        else:
            return render_template('mollie/success.htm', message=message)

    return False


@blueprint.route('/export/', methods=['GET'])
def export_activities():
    activities = Activity.query.filter(
        Activity.end_time >
        (datetime.datetime.now() - datetime.timedelta(hours=12))
    ).order_by(Activity.start_time.asc()).all()
    return jsonify(data=serialize_sqla(activities))
