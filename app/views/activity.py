import datetime

from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for, abort, \
    jsonify
from flask_babel import _  # gettext
from flask_login import current_user
from werkzeug.contrib.atom import AtomFeed

# this is now uncommented for breaking activity for some reason
# please some one check out what is happening
import app.utils.google as google
from app import db
from app.decorators import require_role
from app.forms.activity import ActivityForm, CreateForm
from app.forms.user import SignInForm
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult
from app.models.education import Education
from app.models.mollie import Transaction, TransactionActivity
from app.roles import Roles
from app.service import role_service, file_service
from app.utils import mollie
from app.utils.serialize_sqla import serialize_sqla
from app.enums import FileCategory

blueprint = Blueprint('activity', __name__, url_prefix='/activities')

PICTURE_DIR = 'app/static/activity_pictures/'


# Overview of activities
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<string:archive>/', methods=['GET', 'POST'])
@blueprint.route('/list/<int:page_nr>/', methods=['GET', 'POST'])
@blueprint.route('/list/<string:archive>/<int:page_nr>/',
                 methods=['GET', 'POST'])
def view(archive=None, page_nr=1):
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

    can_write = role_service.user_has_role(current_user,
                                           Roles.ACTIVITY_WRITE)
    return render_template('activity/view.htm',
                           activities=activities.paginate(page_nr, 10, False),
                           archive=archive, title=title, can_write=can_write)


@blueprint.route('/remove/<int:activity_id>/', methods=['POST'])
@require_role(Roles.ACTIVITY_WRITE)
def remove_activity(activity_id=0):
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
    """Activity register and update endpoint.

    Register and update for an activity, with handling of custom forms
    and payment.
    """
    activity = Activity.query.get_or_404(activity_id)

    form = ActivityForm(request.form, obj=current_user)

    # Add education for activity form
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    # Set the number of extra attendees
    if activity.form:
        form.introductions.choices = [(0, _('None'))] + [
            (x, "+%d" % x) for x in range(1, activity.form.introductions + 1)]
        form.introductions.default = (0, _('None'))

    auto_open_register_pane = False

    def render(num_extra_attendees=None):
        can_write = role_service.user_has_role(current_user,
                                               Roles.ACTIVITY_WRITE)
        return render_template(
            'activity/view_single.htm', activity=activity, form=form,
            login_form=SignInForm(), title=activity.name,
            auto_open_register=auto_open_register_pane, can_write=can_write,
            num_extra_attendees=num_extra_attendees)

    # Check if there is a custom_form for this activity
    if not activity.form_id:
        # No form, so no registering and handling thereof required.
        return render()

    # You cannot register when you're not a member of via yet.
    if not current_user.has_paid:
        activity.info = _("You have to be a registered member of "
                          "via in order to register for "
                          "activities. If you believe you are a "
                          "member, please contact the board.")
        return render()

    # Check all attendees including extra attendees
    over_max_registrations = activity.form.attendants >= \
        activity.form.max_attendants

    all_form_results = CustomFormResult.query \
        .filter(CustomFormResult.form_id == activity.form_id)

    # Result for the form, may be None if not entered yet.
    form_result = all_form_results \
        .filter(CustomFormResult.owner_id == current_user.id).first()

    # Not filled in, show over limit message or not and let the user register.
    if not form_result:
        if over_max_registrations:
            activity.info = _("The activity has reached its maximum "
                              "number of registrations. You will be "
                              "placed on the reserves list.")
        return render()

    # Set the previous amount of extra attendees
    form.introductions.data = form_result.introductions

    activity.form_data = form_result.data.replace('"', "'")

    auto_open_register_pane = True

    # You're attending if you're on the form results list within the
    # max attendants count.
    is_attending = bool(all_form_results.limit(activity.form.max_attendants)
                        .from_self().filter(
        CustomFormResult.owner_id == current_user.id).first())

    # Payment still required if you're attending, the form says it costs money
    # and you haven't paid yet.
    form_costs_money = form_result.form.price > 0
    payment_required = form_costs_money and is_attending and \
        not form_result.has_paid

    if is_attending:
        introductions = form_result.introductions
    else:
        introductions = None

    if payment_required:
        form.show_pay_button = True
        form.form_result = form_result

    if not payment_required:
        activity.info = \
            _("Your registration has been completed.") + " " + \
            _("You can edit your registration by resubmitting the form.")
    elif is_attending:

        # TODO If paid, make extra attendees read-only

        activity.info = _("You have successfully registered, "
                          "payment is still required!")

        if form_result.form.requires_direct_payment:
            pay_url = url_for('activity.create_mollie_transaction',
                              result_id=form.form_result.id)

            return redirect(pay_url)
    else:
        activity.info = _("The activity has reached its maximum "
                          "number of registrations. You have been "
                          "placed on the reserves list.")

    return render(num_extra_attendees=introductions)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:activity_id>/', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def create(activity_id=None):
    if activity_id:

        activity = Activity.query.get(activity_id)

        if not activity:
            abort(404)

        title = _("Edit") + " " + str(activity.name)
    else:
        activity = Activity()
        title = _('Create activity')

    form = CreateForm(request.form, obj=activity)

    if request.method == 'POST':

        if form.validate_on_submit():
            form.populate_obj(activity)

            # Facebook ID location, not used yet
            activity.venue = 1

            # Set a custom_form if it actually exists
            form_id = int(form.form_id.data)
            if form_id == 0:
                form_id = None

            activity.form_id = form_id
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

            file = request.files.get('picture')

            if file and file.filename:
                picture = file_service.add_file(FileCategory.ACTIVITY_PICTURE,
                                                file, file.filename)

                old_picture_id = activity.picture_file_id
                activity.picture_file_id = picture.id

                if old_picture_id:
                    old_picture = file_service.get_file_by_id(old_picture_id)
                    file_service.delete_file(old_picture)

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
    transaction = Transaction.query.join(TransactionActivity) \
        .filter(TransactionActivity.custom_form_result_id == form_result.id) \
        .filter(Transaction.status == 'open').first()

    # If no such payment exist, create a new one.
    if not transaction or not transaction.mollie_id:
        callback = TransactionActivity()
        callback.custom_form_result_id = result_id
        db.session.add(callback)
        db.session.commit()

        # Calculate the price with extra attendees
        price = form_result.form.price * (form_result.introductions + 1)

        payment_url, msg = mollie.create_transaction(
            amount=price,
            description=form_result.form.name,
            user=form_result.owner,
            callbacks=[callback]
        )

        return redirect(payment_url) if payment_url else \
            render_template('mollie/success.htm', message=msg)
    else:
        payment, msg = mollie.check_transaction(transaction)
        if not payment:
            return render_template('mollie/fail.htm', message=msg)
        elif payment.is_open():
            return redirect(payment.get_payment_url())
        elif payment.is_paid():
            # TODO: redirect back to activity
            return render_template('mollie/success.htm', message=msg)
        else:
            return render_template('mollie/success.htm', message=msg)


@blueprint.route('/export/', methods=['GET'])
def export_activities():
    activities = Activity.query.filter(
        Activity.end_time >
        (datetime.datetime.now() - datetime.timedelta(hours=12))
    ).order_by(Activity.start_time.asc()).all()
    return jsonify(data=serialize_sqla(activities))


@blueprint.route('/rss/', methods=['GET'])
@blueprint.route('/rss/<string:locale>/')
def rss(locale='en'):
    name = 'via activiteiten' if locale == 'nl' else 'via activities'
    feed = AtomFeed(name, feed_url=request.url, url=request.url_root)
    activities = Activity.query.filter(
        Activity.end_time >
        (datetime.datetime.now() - datetime.timedelta(hours=12))
    ).order_by(Activity.start_time.asc()).all()

    for activity in activities:
        name, description = activity.get_localized_name_desc(locale)
        feed.add(name, description, id=activity.id, content_type='markdown',
                 updated=activity.updated_time, published=activity.start_time,
                 url=url_for('activity.get_activity', activity_id=activity.id))

    return feed.get_response()


@blueprint.route('/picture/<int:activity_id>/')
def picture(activity_id):
    activity = Activity.query.get_or_404(activity_id)

    if activity.picture_file_id is None:
        return redirect('/static/img/via_thumbnail.png')

    picture_file = file_service.get_file_by_id(activity.picture_file_id)

    fn = 'activity_picture_' + activity.name

    content = file_service.get_file_content(picture_file)
    headers = file_service.get_file_content_headers(picture_file,
                                                    display_name=fn)

    return content, headers
