from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, jsonify
from flask_babel import lazy_gettext as _

from app import db
from app.decorators import require_role
from app.forms.location import LocationForm
from app.models.location import Location
from app.roles import Roles
from app.service import role_service
from app.utils.serialize_sqla import serialize_sqla

blueprint = Blueprint('location', __name__, url_prefix='/locations')


@blueprint.route('/<int:location_id>/contacts/', methods=['GET'])
@require_role(Roles.VACANCY_READ)
def get_contacts(location_id):
    location = Location.query.get(location_id)
    return jsonify(contacts=serialize_sqla(location.contacts.all()))


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_READ)
def list(page_nr=1):
    locations = Location.query.paginate(page_nr, 15, False)
    can_write = role_service.user_has_role(Roles.VACANCY_WRITE)
    return render_template('location/list.htm', locations=locations,
                           can_write=can_write)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:location_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def edit(location_id=None):
    """FRONTEND, Create, view or edit a location."""

    # Select location..
    if location_id:
        location = Location.query.get(location_id)
    else:
        location = Location()

    form = LocationForm(request.form, location)

    if form.validate_on_submit():
        form.populate_obj(location)
        db.session.add(location)
        db.session.commit()
        flash(_('Location saved.'), 'success')
        return redirect(url_for('location.edit', location_id=location.id))

    can_write = role_service.user_has_role(Roles.VACANCY_WRITE)
    return render_template('location/edit.htm', location=location, form=form,
                           can_write=can_write)


@blueprint.route('/delete/<int:location_id>/', methods=['POST'])
@require_role(Roles.VACANCY_WRITE)
def delete(location_id):
    """Delete a location."""

    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    flash(_('Location deleted.'), 'success')
    return redirect(url_for('location.list'))
