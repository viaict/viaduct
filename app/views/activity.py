import datetime

# this is now uncommented for breaking activity for some reason
# please some one check out what is happening
import app.utils.google as google

from flask import flash, redirect, render_template, request, url_for, abort,\
    jsonify
from flask import Blueprint
from flask_login import current_user
from flask_babel import _  # gettext

from app import db
from app.forms.activity import ActivityForm, CreateForm
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult
from app.models.mollie import Transaction, TransactionActivity
from app.utils.module import ModuleAPI
from app.utils.file import file_upload, file_remove
from app.utils import mollie
from app.models.education import Education
from app.forms import SignInForm

from app.utils.serialize_sqla import serialize_sqla

blueprint = Blueprint('activity', __name__, url_prefix='/activities')

PICTURE_DIR = 'app/static/activity_pictures/'


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

    activity = Activity.query.get_or_404(activity_id)

    form = ActivityForm(request.form, current_user)

    # Add education for activity form
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    # Check if there is a custom_form for this activity
    if activity.form_id:
        # Count current attendants for "reserved" message
        entries = CustomFormResult.query.filter(CustomFormResult.form_id ==
                                                activity.form_id)
        activity.num_attendants = entries.count()

        # Check if the current user has already entered data in this custom
        # form
        if current_user.is_authenticated and current_user.has_paid:
            all_form_results = CustomFormResult.query \
                .filter(CustomFormResult.form_id == activity.form_id)
            form_result = all_form_results \
                .filter(CustomFormResult.owner_id == current_user.id).first()
            attending = all_form_results.limit(activity.form.max_attendants) \
                .from_self() \
                .filter(CustomFormResult.owner_id == current_user.id).first()

            if form_result:
                activity.form_data = form_result.data.replace('"', "'")
                if not form_result.has_paid and attending:
                    # There is 35 cents administration fee
                    if form_result.form.price - 0.35 > 0:
                        print("tesT")
                        form.show_pay_button = True
                        form.form_result = form_result

                if form_result.has_paid or \
                        (attending and activity.price.lower()
                            in ["gratis", "free", "0"]):
                    activity.info = _("Your registration has been completed.")\
                        + " " \
                        + _("You can edit your registration by resubmitting"
                            " the form.")
                elif attending:
                    activity.info = _("You have successfully registered"
                                      ", payment is still required!")
                else:
                    activity.info = _("The activity has reached its maximum "
                                      "number of registrations. You have been "
                                      "placed on the reserves list.")
            else:
                if activity.num_attendants >= activity.form.max_attendants:
                    activity.info = _("The activity has reached its maximum "
                                      "number of registrations. You will be "
                                      "placed on the reserves list.")
        else:
            activity.info = _("You have to be a registered member of "
                              "via in order to register for "
                              "activities. If you believe you are a "
                              "member, please contact the board.")

    return render_template('activity/view_single.htm', activity=activity,
                           form=form, login_form=SignInForm(),
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

    if request.method == 'POST':

        if form.validate_on_submit():

            act_picture = activity.picture

            form.populate_obj(activity)

            file = request.files['picture']

            if file.filename:
                image = file_upload(file, PICTURE_DIR, True)
                if image:
                    picture = image.name
                else:
                    picture = None

                # Remove old picture
                if act_picture:
                    file_remove(act_picture, PICTURE_DIR)

            elif not picture:
                picture = None

            # Facebook ID location, not used yet
            activity.venue = 1

            # Set a custom_form if it actually exists
            form_id = int(form.form_id.data)
            if form_id == 0:
                form_id = None

            activity.form_id = form_id

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

    return render_template('activity/edit.htm', activity=activity, form=form,
                           title=title)


@blueprint.route('/transaction/<int:result_id>/', methods=['GET', 'POST'])
def create_mollie_transaction(result_id):

    # Find the form_result we are trying to pay.
    form_result = CustomFormResult.query.get_or_404(result_id)

    # Search open transactions that are still waiting to be paid.
    transaction = Transaction.query.join(TransactionActivity)\
        .filter(TransactionActivity.custom_form_result_id == form_result.id)\
        .filter(Transaction.status == 'open').first()

    # If no such payment exist, create a new one.
    if not transaction or not transaction.mollie_id:
        callback = TransactionActivity()
        callback.custom_form_result_id = result_id
        db.session.add(callback)
        db.session.commit()

        payment_url, msg = mollie.create_transaction(
            amount=form_result.form.price,
            description=form_result.form.name,
            user=form_result.owner,
            callbacks=[callback]
        )

        return redirect(payment_url) if payment_url else \
            render_template('mollie/success.htm', message=msg)
    else:
        payment, msg = mollie.check_transaction(transaction)
        if payment.is_open():
            return redirect(payment.get_payment_url())
        else:
            render_template('mollie/success.htm', message=msg)


@blueprint.route('/export/', methods=['GET'])
def export_activities():
    activities = Activity.query.filter(
        Activity.end_time >
        (datetime.datetime.now() - datetime.timedelta(hours=12))
    ).order_by(Activity.start_time.asc()).all()
    return jsonify(data=serialize_sqla(activities))
