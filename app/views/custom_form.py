from urllib.parse import parse_qsl

from flask import (flash, redirect, render_template, request, url_for, abort,
                   jsonify, Blueprint, Response)
from flask_login import current_user

from app import db, constants
from app.decorators import require_role, require_membership
from app.forms import init_form
from app.forms.custom_form import CreateForm
from app.forms.custom_form import AddRegistrationForm
from app.models.custom_form import CustomForm, CustomFormResult, \
    CustomFormFollower
from app.roles import Roles
from app.service import role_service
from app.utils import copernica
from app.utils.forms import flash_form_errors
from app.utils.serialize_sqla import serialize_sqla
import app.service.user_service as user_service

blueprint = Blueprint('custom_form', __name__, url_prefix='/forms')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def view(page_nr=1):
    followed_forms = CustomForm.qry_followed().all()
    active_forms = CustomForm.qry_active().all()
    archived_paginate = CustomForm.qry_archived().paginate(page_nr, 10)

    can_write = role_service.user_has_role(current_user, Roles.ACTIVITY_WRITE)
    return render_template('custom_form/overview.htm',
                           followed_forms=followed_forms,
                           active_forms=active_forms,
                           archived_paginate=archived_paginate,
                           page_nr=page_nr,
                           can_write=can_write)


@blueprint.route('/view/<int:form_id>', methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def view_single(form_id=None):
    custom_form = CustomForm.query.get(form_id)

    if not custom_form:
        return abort(403)

    results = []
    entries = CustomFormResult.query \
        .filter(CustomFormResult.form_id == form_id).order_by("created")

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
def export(form_id):
    # Create the headers
    xp = CustomForm.exports
    xp_names = list(xp.keys())
    names = list(request.form.keys())

    form = CustomForm.query.get(form_id)

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
def create(form_id=None):
    if form_id:
        custom_form = CustomForm.query.get_or_404(form_id)
        prev_max = custom_form.max_attendants
    else:
        custom_form = CustomForm()

    form = init_form(CreateForm, obj=custom_form)

    if request.method == 'POST':
        custom_form.name = form.name.data
        custom_form.origin = form.origin.data
        custom_form.html = form.html.data
        custom_form.msg_success = form.msg_success.data
        custom_form.max_attendants = form.max_attendants.data
        custom_form.introductions = form.introductions.data
        if form.price.data is None:
            form.price.data = 0.0
        custom_form.price = form.price.data
        custom_form.terms = form.terms.data
        custom_form.requires_direct_payment = form.requires_direct_payment.data

        follower = None

        if not form_id:
            follower = CustomFormFollower(owner_id=current_user.id)
            flash('You\'ve created a form successfully.', 'success')

        else:
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
                            copernica.SUBPROFILE_ACTIVITY, sub.owner_id,
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
                            copernica.SUBPROFILE_ACTIVITY, sub.owner_id,
                            sub.form_id, copernica_data)

        db.session.add(custom_form)
        db.session.commit()

        if follower is not None:
            follower.form_id = custom_form.id
            db.session.add(follower)
            db.session.commit()

        return redirect(url_for('custom_form.view'))
    else:
        flash_form_errors(form)

    return render_template('custom_form/create.htm', form=form)


@blueprint.route('/remove/<int:submit_id>', methods=['POST'])
@require_role(Roles.ACTIVITY_WRITE)
def remove_response(submit_id=None):
    response = "success"

    # Test if user already signed up
    submission = CustomFormResult.query.filter(
        CustomFormResult.id == submit_id
    ).first()

    if not submission:
        abort(404)

    form_id = submission.form_id
    max_attendants = submission.form.max_attendants

    db.session.delete(submission)
    db.session.commit()

    all_sub = CustomFormResult.query.filter(
        CustomFormResult.form_id == form_id
    ).all()

    if max_attendants <= len(all_sub):
        from_list = all_sub[max_attendants - 1]
        copernica_data = {
            "Reserve": "Nee"
        }
        copernica.update_subprofile(
            copernica.SUBPROFILE_ACTIVITY, from_list.owner_id,
            from_list.form_id, copernica_data)

    return response


# Ajax method
@blueprint.route('/submit/<int:form_id>', methods=['POST'])
@require_membership
def submit(form_id=-1):
    # TODO make sure custom_form rights are set on server
    response = "success"

    custom_form = CustomForm.query.get(form_id)
    if not custom_form:
        return "error", 404

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
    duplicate_test = CustomFormResult.query.filter(
        CustomFormResult.owner_id == user.id,
        CustomFormResult.form_id == form_id
    ).first()

    if duplicate_test:
        result = duplicate_test
        result.data = request.form['data']
        response = "edit"
    else:
        entries = CustomFormResult.query \
            .filter(CustomFormResult.form_id == form_id)
        num_attendants = sum(entry.introductions + 1 for entry in
                             entries.all())
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
            copernica.add_subprofile(copernica.SUBPROFILE_ACTIVITY,
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
def follow(form_id, page_nr=1):
    # Unfollow if re-submitted
    follows = (current_user.custom_forms_following
               .filter(CustomFormFollower.form_id == form_id)
               .first())

    if follows:
        flash('Formulier ontvolgd', 'success')
        db.session.delete(follows)
    else:
        flash('Formulier gevolgd', 'success')
        result = CustomFormFollower(current_user.id, form_id)
        db.session.add(result)

    db.session.commit()

    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/archive/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/archive/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def archive(form_id, page_nr=1):
    form = CustomForm.query.get_or_404(form_id)

    form.archived = True
    db.session.commit()

    flash('Formulier gearchiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/unarchive/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/unarchive/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
@require_role(Roles.ACTIVITY_WRITE)
def unarchive(form_id, page_nr=1):
    form = CustomForm.query.get_or_404(form_id)

    form.archived = False
    db.session.commit()

    flash('Formulier gede-archiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


# Ajax endpoint
@blueprint.route('/has_paid/<int:submit_id>', methods=['POST'])
@require_role(Roles.FINANCIAL_ADMIN)
def has_paid(submit_id=None):
    # Test if user already signed up
    submission = CustomFormResult.query.filter(
        CustomFormResult.id == submit_id
    ).first()

    if not submission:
        abort(404)
        return

    # Adjust the "has_paid"
    submission.has_paid = not submission.has_paid

    db.session.add(submission)
    db.session.commit()

    copernica_data = {
        "Betaald": "Ja" if submission.has_paid else "Nee",
    }

    copernica.update_subprofile(copernica.SUBPROFILE_ACTIVITY,
                                submission.owner_id, submission.form_id,
                                copernica_data)

    return "success"


# TODO: Move to API.
@blueprint.route('/loader/<int:current>/', methods=['GET'])
def loader(current):
    try:
        current = int(current)
    except ValueError:
        return abort(404)

    return jsonify(forms=serialize_sqla(CustomForm.aslist(current)))
