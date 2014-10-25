from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort

from viaduct import db
from viaduct.models.contact import Contact
from viaduct.models.location import Location
from viaduct.utilities import validate_form
from viaduct.forms import ContactForm
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('contact', __name__, url_prefix='/contacts')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
    '''
    Show a paginated list of contacts.
    '''
    if not GroupPermissionAPI.can_read('contact'):
        return abort(403)

    contacts = Contact.query.paginate(page, 15, False)
    return render_template('contact/list.htm', contacts=contacts)


@blueprint.route('/create/', methods=['GET'])
@blueprint.route('/edit/<int:contact_id>/', methods=['GET'])
def edit(contact_id=None):
    '''
    Create or edit a contact, frontend.
    '''
    if not GroupPermissionAPI.can_read('contact'):
        return abort(403)

    if contact_id:
        contact = Contact.query.get(contact_id)
    else:
        contact = Contact()

    form = ContactForm(request.form, contact)

    locations = Location.query.order_by('address').order_by('city')
    form.location_id.choices = \
        [(l.id, '%s, %s' % (l.address, l.city)) for l in locations]

    return render_template('contact/edit.htm', contact=contact, form=form)


@blueprint.route('/create/', methods=['POST'])
@blueprint.route('/edit/<int:contact_id>/', methods=['POST'])
def update(contact_id=None):
    '''
    Create or edit a contact, backend.
    '''
    if not GroupPermissionAPI.can_write('contact'):
        return abort(403)

    if contact_id:
        contact = Contact.query.get(contact_id)
    else:
        contact = Contact()

    form = ContactForm(request.form, contact)
    if not validate_form(form, ['name', 'email', 'phone_nr', 'location_id']):
        return redirect(url_for('contact.edit', contact_id=contact_id))

    form.populate_obj(contact)
    db.session.add(contact)
    db.session.commit()

    if contact_id:
        flash('Contactpersoon opgeslagen', 'success')
    else:
        contact_id = contact.id
        flash('Contactpersoon aangemaakt', 'success')

    return redirect(url_for('contact.edit', contact_id=contact_id))


@blueprint.route('/delete/<int:contact_id>/', methods=['POST'])
def delete(contact_id):
    '''
    Delete a contact.
    '''
    if not GroupPermissionAPI.can_write('contact'):
        return abort(403)

    contact = Contact.query.get(contact_id)
    if not contact:
        return abort(404)

    db.session.delete(contact)
    db.session.commit()
    flash('Contactpersoon verwijderd', 'success')

    return redirect(url_for('contact.list'))
