from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort
from flask_babel import lazy_gettext as _

from app import db
from app.models.contact import Contact
from app.models.location import Location
from app.forms import ContactForm
from app.utils.module import ModuleAPI

blueprint = Blueprint('contact', __name__, url_prefix='/contacts')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def list(page_nr=1):
    """Show a paginated list of contacts."""
    if not ModuleAPI.can_read('contact'):
        return abort(403)

    contacts = Contact.query.paginate(page_nr, 15, False)
    return render_template('contact/list.htm', contacts=contacts)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:contact_id>/', methods=['GET', 'POST'])
def edit(contact_id=None):
    """Create or edit a contact, frontend."""
    if not ModuleAPI.can_write('contact'):
        return abort(403)

    if contact_id:
        contact = Contact.query.get(contact_id)
    else:
        contact = Contact()

    form = ContactForm(request.form, contact)

    locations = Location.query.order_by(
        Location.address).order_by(Location.city)
    form.location_id.choices = \
        [(l.id, '%s, %s' % (l.address, l.city)) for l in locations]

    if form.validate_on_submit():
        if not contact.id and Contact.query.filter(
                Contact.email == form.email.data).count():
            flash(_('Contact email "%s" is already in use.' %
                    form.email.data), 'danger')
            return render_template('contact/edit.htm', contact=contact,
                                   form=form)
        form.populate_obj(contact)
        db.session.add(contact)
        db.session.commit()
        flash(_('Contact person saved.'), 'success')
        return redirect(url_for('contact.edit', contact_id=contact.id))

    return render_template('contact/edit.htm', contact=contact, form=form)


@blueprint.route('/delete/<int:contact_id>/', methods=['POST'])
def delete(contact_id):
    """Delete a contact."""
    if not ModuleAPI.can_write('contact'):
        return abort(403)

    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash(_('Contact person deleted.'), 'success')

    return redirect(url_for('contact.list'))
