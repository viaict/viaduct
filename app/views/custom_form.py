from flask import (flash, redirect, render_template, request, url_for, abort,
                   jsonify, Blueprint, Response)
from flask_login import current_user

from app import db
from app.utils import serialize_sqla
from app.utils.forms import flash_form_errors
from app.forms.custom_form import CreateForm
from app.models.custom_form import CustomForm, CustomFormResult, \
    CustomFormFollower
from app.utils.module import ModuleAPI

from app.utils import copernica
from urllib.parse import parse_qsl


blueprint = Blueprint('custom_form', __name__, url_prefix='/forms')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def view(page_nr=1):
    if not ModuleAPI.can_read('custom_form'):
        return abort(403)

    followed_forms = CustomForm.qry_followed().all()
    active_forms = CustomForm.qry_active().all()
    archived_paginate = CustomForm.qry_archived().paginate(page_nr, 10)

    return render_template('custom_form/overview.htm',
                           followed_forms=followed_forms,
                           active_forms=active_forms,
                           archived_paginate=archived_paginate,
                           page_nr=page_nr)


@blueprint.route('/view/<int:form_id>', methods=['GET', 'POST'])
def view_single(form_id=None):
    if not ModuleAPI.can_read('custom_form'):
        return abort(403)

    custom_form = CustomForm.query.get(form_id)

    if not custom_form:
        return abort(403)

    results = []
    entries = CustomFormResult.query\
        .filter(CustomFormResult.form_id == form_id).order_by("created")

    from urllib.parse import unquote_plus
    from urllib.parse import parse_qs

    for entry in entries:
        # Hide form entries from non existing users
        data = parse_qs(entry.data)

        # Add the entry date
        time = entry.created.strftime("%Y-%m-%d %H:%M") if \
            entry.created is not None else ""

        # Append the results with a single entry
        results.append({
            'id': entry.id,
            'owner': entry.owner,
            'data': data,
            'has_payed': entry.has_payed,
            'time': time
        })

    custom_form.results = results

    return render_template('custom_form/view_results.htm',
                           custom_form=custom_form,
                           xps=CustomForm.exports,
                           unquote_plus=unquote_plus)


@blueprint.route('/export/<int:form_id>/', methods=['POST'])
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
def create(form_id=None):
    if not ModuleAPI.can_write('custom_form') or current_user.is_anonymous:
        return abort(403)

    if form_id:
        custom_form = CustomForm.query.get_or_404(form_id)
        prev_max = custom_form.max_attendants
        if not custom_form:
            abort(404)
    else:
        custom_form = CustomForm()

    form = CreateForm(request.form, custom_form)

    if request.method == 'POST':
        custom_form.name = form.name.data
        custom_form.origin = form.origin.data
        custom_form.html = form.html.data
        custom_form.msg_success = form.msg_success.data
        custom_form.max_attendants = form.max_attendants.data
        if form.price.data is None:
            form.price.data = 0.0
        custom_form.price = form.price.data
        custom_form.transaction_description = form.transaction_description.data
        custom_form.terms = form.terms.data

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
                    for x in range(prev_max, max(cur_max, len(all_sub) - 1)):
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
def remove_response(submit_id=None):
    response = "success"

    if not ModuleAPI.can_read('custom_form'):
        return abort(403)

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


@blueprint.route('/submit/<int:form_id>', methods=['POST'])
def submit(form_id=-1):
    # TODO make sure custom_form rights are set on server
    if not ModuleAPI.can_read('activity') or current_user.is_anonymous:
        return "error", 403

    response = "success"

    custom_form = CustomForm.query.get(form_id)
    if not custom_form:
        return "error", 404
    if not custom_form.submittable_by(current_user):
        return "error", 403

    # These fields might be there
    try:
        if request.form['phone_nr']:
            current_user.phone_nr = request.form['phone_nr']

        if request.form['noodnummer']:
            current_user.emergency_phone_nr = request.form['noodnummer']

        if request.form['shirt_maat']:
            current_user.shirt_size = request.form['shirt maat']

        if request.form['dieet[]']:
            current_user.diet = ', '.join(request.form['dieet[]'])

        if request.form['allergie/medicatie']:
            current_user.allergy = request.form['allergie/medicatie']

        if request.form['geslacht']:
            current_user.gender = request.form['geslacht']
    except Exception:
        pass

    # Test if current user already signed up
    duplicate_test = CustomFormResult.query.filter(
        CustomFormResult.owner_id == current_user.id,
        CustomFormResult.form_id == form_id
    ).first()

    if duplicate_test:
        result = duplicate_test
        result.data = request.form['data']
        response = "edit"
    else:
        entries = CustomFormResult.query\
            .filter(CustomFormResult.form_id == form_id)
        num_attendants = entries.count()

        result = CustomFormResult(current_user.id, form_id,
                                  request.form['data'])

        # Check if number attendants allows another registration
        if num_attendants >= custom_form.max_attendants:
            # Create "Reserve" signup
            response = "reserve"
        else:
            copernica_data = {
                "Naam": custom_form.name,
                "Betaald": result.has_payed,
                "Bedrag": custom_form.price,
                "viaductID": form_id,
                "Reserve": "Ja" if response is "reserve" else "Nee",
            }
            copernica.add_subprofile(copernica.SUBPROFILE_ACTIVITY,
                                     current_user.id, copernica_data)

    db.session.add(current_user)
    db.session.commit()

    db.session.add(result)
    db.session.commit()

    return response


@blueprint.route('/follow/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/follow/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
def follow(form_id, page_nr=1):
    if not ModuleAPI.can_write('custom_form') or current_user.is_anonymous:
        return abort(403)

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
def archive(form_id, page_nr=1):
    if not ModuleAPI.can_write('custom_form') or current_user.is_anonymous:
        return abort(403)

    form = CustomForm.query.get(form_id)
    if not form:
        return abort(404)

    form.archived = True
    db.session.commit()

    flash('Formulier gearchiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/unarchive/<int:form_id>/', methods=['GET', 'POST'])
@blueprint.route('/unarchive/<int:form_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
def unarchive(form_id, page_nr=1):
    if not ModuleAPI.can_write('custom_form') or current_user.is_anonymous:
        return abort(403)

    form = CustomForm.query.get(form_id)
    if not form:
        return abort(404)

    form.archived = False
    db.session.commit()

    flash('Formulier gede-archiveerd', 'success')

    return redirect(url_for('custom_form.view', page_nr=page_nr))


@blueprint.route('/has_payed/<int:submit_id>', methods=['POST'])
def has_payed(submit_id=None):
    response = "success"

    if not ModuleAPI.can_write('custom_form') or current_user.is_anonymous:
        return abort(403)

    # Test if user already signed up
    submission = CustomFormResult.query.filter(
        CustomFormResult.id == submit_id
    ).first()

    if not submission:
        response = "Error, submission could not be found"

    # Adjust the "has_payed"
    if submission.has_payed:
        submission.has_payed = False
    else:
        submission.has_payed = True

    db.session.add(submission)
    db.session.commit()

    copernica_data = {
        "Betaald": "Ja" if submission.has_payed else "Nee",
    }

    copernica.update_subprofile(copernica.SUBPROFILE_ACTIVITY,
                                submission.owner_id, submission.form_id,
                                copernica_data)

    return response


# TODO: Move to API.
@blueprint.route('/loader/', methods=['GET'])
def loader():
    try:
        current = int(request.args.get('current'))
    except ValueError:
        current = None

    return jsonify(forms=serialize_sqla(CustomForm.aslist(current)))
