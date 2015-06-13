from flask import flash, redirect, render_template, request, url_for, abort
from flask import Blueprint, Response
from flask.ext.login import current_user

from viaduct import db
from viaduct.helpers import flash_form_errors
from viaduct.forms.custom_form import CreateForm
from viaduct.models.user import User
from viaduct.models.custom_form import CustomForm, CustomFormResult, \
    CustomFormFollower
from viaduct.api.module import ModuleAPI

from sqlalchemy import desc
from urllib.parse import parse_qsl

import io
import csv

blueprint = Blueprint('custom_form', __name__, url_prefix='/forms')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/page', methods=['GET', 'POST'])
@blueprint.route('/page/', methods=['GET', 'POST'])
def view():
    page = request.args.get('page_nr', '')

    if not page:
        page = 1
    else:
        page = int(page)

    if not ModuleAPI.can_write('custom_form'):
        return abort(403)

    custom_forms = CustomForm.query.order_by(desc("id"))

    if current_user and current_user.id > 0:
        follows = CustomFormFollower.query\
            .filter(CustomFormFollower.owner_id == current_user.id).all()

        ids = []

        for follow in follows:
            ids.append(follow.form_id)

        followed_forms = CustomForm.query.filter(CustomForm.id.in_(ids)).all()
    else:
        followed_forms = []
        ids = []

    # TODO Custom forms for specific groups (i.e coordinator can only see own
    # forms)
    return render_template('custom_form/overview.htm',
                           custom_forms=custom_forms.paginate(page, 20, False),
                           followed_forms=followed_forms, followed_ids=ids)


@blueprint.route('/view/<int:form_id>', methods=['GET', 'POST'])
def view_single(form_id=None):
    if not ModuleAPI.can_write('custom_form'):
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
        time = entry.created.strftime("%Y-%m-%d %H:%I") if \
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

    # Write all the values to the io field
    str_io = io.StringIO()
    wrt = csv.DictWriter(str_io, fieldnames=label_set)
    wrt.writeheader()
    wrt.writerows(csv_rows)

    def generate():
        yield str_io.getvalue()

    return Response(generate(), mimetype='text/csv')


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:form_id>', methods=['GET', 'POST'])
def create(form_id=None):
    if not ModuleAPI.can_write('custom_form'):
        return abort(403)

    if form_id:
        custom_form = CustomForm.query.get(form_id)

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

        if not form_id:
            flash('You\'ve created a form successfully.', 'success')
        else:
            flash('You\'ve updated a form successfully.', 'success')

        db.session.add(custom_form)
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

    db.session.delete(submission)
    db.session.commit()

    return response


@blueprint.route('/submit/<int:form_id>', methods=['POST'])
def submit(form_id=None):
    # TODO make sure custom_form rights are set on server
    if not ModuleAPI.can_read('custom_form'):
        return abort(403)

    response = "success"

    if form_id:
        custom_form = CustomForm.query.get(form_id)

        if not custom_form:
            abort(404)

        # Logged in user
        if current_user and current_user.id > 0:
            user = User.query.get(current_user.id)
        else:
            # Need to be logged in
            return abort(403)

    if not user:
        response = "error"
    else:
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

        # Test if user already signed up
        duplicate_test = CustomFormResult.query.filter(
            CustomFormResult.owner_id == user.id,
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

            # Check if number attendants allows another registration
            if num_attendants >= custom_form.max_attendants:
                # Create "Reserve" signup
                response = "reserve"
            result = CustomFormResult(user.id, form_id,
                                      request.form['data'])

        db.session.add(user)
        db.session.commit()

        db.session.add(result)
        db.session.commit()

    return response


@blueprint.route('/follow/<int:form_id>', methods=['GET', 'POST'])
def follow(form_id=None):
    if not ModuleAPI.can_write('custom_form'):
        return abort(403)

    # Logged in user
    if not current_user or current_user.id <= 0:
        # Need to be logged in
        return abort(403)

    # Unfollow if re-submitted
    follows = CustomFormFollower.query\
        .filter(CustomFormFollower.form_id == form_id).first()

    if follows:
        response = "removed"
        db.session.delete(follows)
    else:
        response = "added"
        result = CustomFormFollower(current_user.id, form_id)
        db.session.add(result)

    db.session.commit()

    return response


@blueprint.route('/has_payed/<int:submit_id>', methods=['POST'])
def has_payed(submit_id=None):
    response = "success"

    if not ModuleAPI.can_write('custom_form'):
        return abort(403)

    # Logged in user
    if not current_user or current_user.id <= 0:
        # Need to be logged in
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

    return response
