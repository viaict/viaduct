from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, jsonify, abort
from flask_babel import lazy_gettext as _

from app import db
from app.models.location import Location
from app.utils.serialize_sqla import serialize_sqla
from app.forms import LocationForm
from app.utils.module import ModuleAPI

blueprint = Blueprint('location', __name__, url_prefix='/locations')


@blueprint.route('/<int:location_id>/contacts/', methods=['GET'])
def get_contacts(location_id):
    if not ModuleAPI.can_read('contacts'):
        return jsonify(error=_('No permissions to read contacts'))

    location = Location.query.get(location_id)
    return jsonify(contacts=serialize_sqla(location.contacts.all()))


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def list(page_nr=1):
    if not ModuleAPI.can_read('location'):
        return abort(403)

    locations = Location.query.paginate(page_nr, 15, False)
    return render_template('location/list.htm', locations=locations)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:location_id>/', methods=['GET', 'POST'])
def edit(location_id=None):
    """FRONTEND, Create, view or edit a location."""
    if not ModuleAPI.can_write('location'):
        return abort(403)

    # Select location..
    if location_id:
        location = Location.query.get(location_id)
    else:
        location = Location()

    form = LocationForm(request.form, obj=location)

    if form.validate_on_submit():
        form.populate_obj(location)
        db.session.add(location)
        db.session.commit()
        flash(_('Location saved.'), 'success')
        return redirect(url_for('location.edit', location_id=location.id))
    return render_template('location/edit.htm', location=location, form=form)


@blueprint.route('/delete/<int:location_id>/', methods=['POST'])
def delete(location_id):
    """Delete a location."""
    if not ModuleAPI.can_write('location'):
        return abort(403)

    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash(_('Location deleted.'), 'success')
    return redirect(url_for('location.list'))
