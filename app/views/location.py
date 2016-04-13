from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, jsonify, abort

from app import db
from app.models.location import Location
from app.utils import serialize_sqla, validate_form
from app.forms import LocationForm
from app.utils.module import ModuleAPI

blueprint = Blueprint('location', __name__, url_prefix='/locations')


@blueprint.route('/<int:location_id>/contacts/', methods=['GET'])
def get_contacts(location_id):
    if not ModuleAPI.can_read('contacts'):
        return jsonify(error='Geen toestemming cotactpersonen te lezen')

    location = Location.query.get(location_id)
    return jsonify(contacts=serialize_sqla(location.contacts.all()))


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
    if not ModuleAPI.can_read('location'):
        return abort(403)

    locations = Location.query.paginate(page, 15, False)
    return render_template('location/list.htm', locations=locations)


@blueprint.route('/create/', methods=['GET'])
@blueprint.route('/edit/<int:location_id>/', methods=['GET'])
def view(location_id=None):
    '''
    FRONTEND
    Create, view or edit a location.
    '''
    if not ModuleAPI.can_read('location'):
        return abort(403)

    # Select location..
    if location_id:
        location = Location.query.get(location_id)
    else:
        location = Location()

    form = LocationForm(request.form, location)
    return render_template('location/view.htm', location=location, form=form)


@blueprint.route('/create/', methods=['POST'])
@blueprint.route('/edit/<int:location_id>/', methods=['POST'])
def update(location_id=None):
    '''
    BACKEND
    Create or edit a location.
    '''
    if not ModuleAPI.can_write('location'):
        return abort(403)

    # Select location.
    if location_id:
        location = Location.query.get(location_id)
    else:
        location = Location()

    form = LocationForm(request.form, location)
    if not validate_form(form, ['city', 'country', 'address', 'zip', 'email',
                                'phone_nr']):
        return redirect(url_for('location.view', location_id=location_id))

    form.populate_obj(location)
    db.session.add(location)
    db.session.commit()

    if location_id:
        flash('Locatie opgeslagen', 'success')
    else:
        location_id = location.id
        flash('Locatie aangemaakt', 'success')

    return redirect(url_for('location.view', location_id=location_id))


@blueprint.route('/delete/<int:location_id>/', methods=['POST'])
def delete(location_id):
    '''
    BACKEND
    Delete a location.
    '''
    if not ModuleAPI.can_write('location'):
        return abort(403)

    location = Location.query.get(location_id)
    if not location:
        return abort(404)

    db.session.delete(location)
    db.session.commit()
    flash('Locatie verwijderd', 'success')

    return redirect(url_for('location.list'))
