from flask import (flash, redirect, render_template, request, url_for, abort,
                   jsonify, Blueprint, Response)
from flask_login import current_user
from functools import wraps
from urllib.parse import parse_qsl

import app.service.user_service as user_service
from app import db, constants, app
from app.decorators import require_role, require_membership
from app.forms import init_form
from app.forms.custom_form import AddRegistrationForm
from app.forms.custom_form import CreateForm
from app.models.custom_form import CustomForm, CustomFormResult
from app.roles import Roles
from app.service import role_service, custom_form_service
from app.utils import copernica
from app.utils.forms import flash_form_errors
from app.utils.pagination import Pagination
from app.utils.serialize_sqla import serialize_sqla

blueprint = Blueprint('custom_form', __name__, url_prefix='/forms')


def require_form_access(f):
    """
    Check whether the user has access to the form.

    NOTE: Assumes that the form_id is the first parameter in the view function.
    """

    @wraps(f)
    def wrapper(form_id, *args, **kwargs):
        if form_id:
            custom_form_service. \
                check_user_can_access_form(form_id, current_user)
        return f(form_id, *args, **kwargs)

    return wrapper


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def view(page_nr=1):
    followed_forms = custom_form_service. \
        get_active_followed_forms_by_user(current_user)
    active_forms = custom_form_service. \
        get_active_unfollowed_by_user(current_user)
    archived_forms = custom_form_service. \
        get_inactive_forms_by_user(current_user)

    archived_paginate = Pagination(page_nr, 10, len(archived_forms),
                                   archived_forms)

    can_write = role_service.user_has_role(current_user, Roles.ACTIVITY_WRITE)
    return render_template('custom_form/overview.htm',
                           followed_forms=followed_forms,
                           active_forms=active_forms,
                           archived_paginate=archived_paginate,
                           page_nr=page_nr,
                           can_write=can_write)


@blueprint.route('/view/<int:form_id>', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def view_single(form_id=None):
    custom_form = custom_form_service.get_form_by_form_id(form_id)

    results = []
    entries = custom_form_service.get_form_entries_by_form_id(form_id)

    from urllib.parse import unquote_plus
    from urllib.parse import parse_qs

    attendants = 0
    for entry in entries:
        # Hide form entries from non existing users
        data = parse_qs(entry.data)

        # Add the entry date
        time = entry.created.strftime(constants.DT_FORMAT) if \
            entry.created is not None else ""

        # Get the total number of attendants including extra attendees
        attendants = attendants + 1 + entry.introductions

        # Append the results with a single entry
        results.append({
            'id': entry.id,
            'owner': entry.owner,
            'data': data,
            'has_paid': entry.has_paid,
            'time': time,
            'introductions': entry.introductions,
            'is_reserve': attendants > custom_form.max_attendants
        })

    custom_form.results = results

    can_update_paid = role_service.\
        user_has_role(current_user, Roles.FINANCIAL_ADMIN)

    add_registration_form = AddRegistrationForm()

    return render_template('custom_form/view_results.htm',
                           add_registration_form=add_registration_form,
                           custom_form=custom_form,
                           xps=CustomForm.exports,
                           unquote_plus=unquote_plus,
                           can_update_paid=can_update_paid)


@blueprint.route('/export/<int:form_id>/', methods=['POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def export(form_id):
    # Create the headers
    xp = CustomForm.exports
    xp_names = list(xp.keys())
    names = list(request.form.keys())

    form = custom_form_service.get_form_by_form_id(form_id)

    # First create a list of key based dictionaries to gather
    # all the different keys in the form
    csv_rows = []
    for r in form.custom_form_results:

        data = {}

        for name in xp_names:
            if name not in names:
                continue

            # Split the custom part of the form in different columns
            if name is 'form':
                # Data from the custom form is saved in querystring format
                export = xp[name]['export'](r)
                qs_dict = dict(parse_qsl(export, keep_blank_values=True))
                data.update(qs_dict)
                continue
            else:
                export = xp[name]['export']
                data.update({name: export(r)})

        csv_rows.append(data)

    # Calculate all the labels in the csv_rows
    label_set = set()
    for i in csv_rows:
        label_set.update(list(i.keys()))

    from io import StringIO
    from csv import DictWriter

    # Write all the values to the io field
    str_io = StringIO()
    wrt = DictWriter(str_io, fieldnames=label_set)
    wrt.writeheader()
    wrt.writerows(csv_rows)

    def generate():
        yield str_io.getvalue()

    return Response(generate(), mimetype='text/csv')


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:form_id>', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def create(form_id=None):
    if form_id:
        custom_form = custom_form_service.get_form_by_form_id(form_id)
        prev_max = custom_form.max_attendants
    else:
        custom_form = CustomForm()

    form = init_form(CreateForm, obj=custom_form)

    if request.method == 'POST':
        custom_form.name = form.name.data
        custom_form.origin = form.origin.data
        custom_form.group = form.group.data
        custom_form.html = form.html.data
        custom_form.msg_success = form.msg_success.data
        custom_form.max_attendants = form.max_attendants.data
        custom_form.introductions = form.introductions.data
        if form.price.data is None:
            form.price.data = 0.0
        custom_form.price = form.price.data
        custom_form.terms = form.terms.data
        custom_form.requires_direct_payment = form.requires_direct_payment.data

        if form_id:
            flash('You\'ve updated a form successfully.', 'success')
            cur_max = int(custom_form.max_attendants)
            # print("Current maximum: " + cur_max)
            # print("Previous maximum: " + prev_max)
            # print("Current submissions: " + len(all_sub))
            if cur_max > prev_max:
                all_sub = CustomFormResult.query.filter(
                    CustomFormResult.form_id == form_id
                ).all()
                # Update for users that were on the reserve list that they
                # can now attend.
                if prev_max < len(all_sub):
                    for x in range(prev_max, min(cur_max, len(all_sub))):
                        sub = all_sub[x]
                        copernica_data = {
                            "Reserve": "Nee"
                        }
                        copernica.update_subprofile(
                            app.config['COPERNICA_ACTIVITEITEN'], sub.owner_id,
                            sub.form_id, copernica_data)
            elif cur_max < prev_max:
                all_sub = CustomFormResult.query.filter(
                    CustomFormResult.form_id == form_id
                ).all()
                if cur_max < len(all_sub):
                    for x in range(cur_max, max(prev_max, len(all_sub) - 1)):
                        sub = all_sub[x]
                        copernica_data = {
                            "Reserve": "Ja"
                        }
                        copernica.update_subprofile(
                            app.config['COPERNICA_ACTIVITEITEN'], sub.owner_id,
                            sub.form_id, copernica_data)

        db.session.add(custom_form)
        db.session.commit()

        if form_id is None:
            flash('You\'ve created a form successfully.', 'success')
            custom_form_service.follow_form(
                form=custom_form, user_id=current_user.id)

        return redirect(url_for('custom_form.view'))
    else:
        flash_form_errors(form)

    return render_template('custom_form/create.htm', form=form)


@blueprint.route('/remove/<int:form_id>/<submission_id>/', methods=['POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def remove_response(form_id=None, submission_id=None):

    response = "success"

    # Test if user already signed up
    submission = custom_form_service.\
        get_form_submission_by_id(form_id, submission_id)

    form_id = submission.form_id
    max_attendants = submission.form.max_attendants

    db.session.delete(submission)
    db.session.commit()

    all_sub = custom_form_service.get_form_entries_by_form_id(form_id)

    if max_attendants <= len(all_sub):
        from_list = all_sub[max_attendants - 1]
        copernica_data = {
            "Reserve": "Nee"
        }
        copernica.update_subprofile(
            app.config['COPERNICA_ACTIVITEITEN'], from_list.owner_id,
            from_list.form_id, copernica_data)

    return response


# Ajax method
@blueprint.route('/submit/<int:form_id>', methods=['POST'])
@require_membership
def submit(form_id=-1):
    # TODO make sure custom_form rights are set on server
    response = "success"

    custom_form = custom_form_service.find_form_by_form_id(form_id)
    if not custom_form:
        return "error", 404

    print(custom_form.submittable_by(current_user))
    if not custom_form.submittable_by(current_user):
        return "error", 403

    if role_service.user_has_role(current_user, Roles.ACTIVITY_WRITE) and \
            'user_id' in request.form:
        user_id = int(request.form['user_id'])
        user = user_service.find_by_id(user_id)
    else:
        user = current_user

    # These fields might be there
    try:
        if request.form['phone_nr']:
            user.phone_nr = request.form['phone_nr']

        if request.form['noodnummer']:
            user.emergency_phone_nr = request.form['noodnummer']

        if request.form['shirt_maat']:
            user.shirt_size = request.form['shirt maat']

        if request.form['dieet[]']:
            user.diet = ', '.join(request.form['dieet[]'])

        if request.form['allergie/medicatie']:
            user.allergy = request.form['allergie/medicatie']

        if request.form['geslacht']:
            user.gender = request.form['geslacht']
    except Exception:
        pass

    # Test if current user already signed up
    duplicate_test = custom_form_service.find_form_submission_by_user_id(
        form_id, user.id)

    if duplicate_test:
        result = duplicate_test
        result.data = request.form['data']
        response = "edit"
    else:
        entries = custom_form_service.get_form_entries_by_form_id(form_id)
        num_attendants = sum(entry.introductions + 1 for entry in entries)
        num_introduce = min(int(request.form.get('introductions', 0)),
                            custom_form.introductions)

        result = CustomFormResult(user.id, form_id,
                                  request.form['data'],
                                  has_paid=False,
                                  introductions=num_introduce)

        # Check if number attendants allows another registration
        if num_attendants >= custom_form.max_attendants:
            # Create "Reserve" signup
            response = "reserve"
        elif num_introduce > custom_form.introductions:
            response = "edit"
        else:
            copernica_data = {
                "Naam": custom_form.name,
                "Betaald": result.has_paid,
                "Bedrag": custom_form.price,
                "viaductID": form_id,
                "Reserve": "Ja" if response is "reserve" else "Nee",
            }
            copernica.add_subprofile(app.config['COPERNICA_ACTIVITEITEN'],
                                     user.id, copernica_data)

    db.session.add(user)
    db.session.commit()

    db.session.add(result)
    db.session.commit()

    return response


@blueprint.route('/follow/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/follow/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def follow(form_id, page_nr=1):
    following = custom_form_service.toggle_form_follow(
        form_id=form_id, user_id=current_user.id)

    if following:
        flash('Formulier gevolgd', 'success')
    else:
        flash('Formulier ontvolgd', 'success')
    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/archive/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/archive/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def archive(form_id, page_nr=1):
    custom_form_service.form_set_archive_status(form_id, True)

    flash('Formulier gearchiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/unarchive/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/unarchive/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
@require_form_access
def unarchive(form_id, page_nr=1):
    custom_form_service.form_set_archive_status(form_id, False)

    flash('Formulier gede-archiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


# Ajax endpoint
@blueprint.route('/has_paid/<int:form_id>/<int:submission_id>/',
                 methods=['POST'])
@require_role(Roles.FINANCIAL_ADMIN)
@require_form_access
def has_paid(form_id=None, submission_id=None):

    custom_form_service.toggle_form_submission_paid(form_id, submission_id)

    return "success"


@blueprint.route('/loader/<int:current>/', methods=['GET'])
def loader(current):
    try:
        current = int(current)
    except ValueError:
        return abort(404)

    return jsonify(forms=serialize_sqla(CustomForm.aslist(current)))
