from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user

from app import db
from app.decorators import require_role
from app.forms.contact import ContactForm
from app.models.contact import Contact
from app.models.location import Location
from app.roles import Roles
from app.service import role_service

blueprint = Blueprint('contact', __name__, url_prefix='/contacts')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_READ)
def list(page_nr=1):
    """Show a paginated list of contacts."""
    contacts = Contact.query.paginate(page_nr, 15, False)
    can_write = role_service.user_has_role(current_user, Roles.VACANCY_WRITE)
    return render_template('contact/list.htm', contacts=contacts,
                           can_write=can_write)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:contact_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def edit(contact_id=None):
    """Create or edit a contact, frontend."""
    if contact_id:
        contact = Contact.query.get(contact_id)
    else:
        contact = Contact()

    form = ContactForm(request.form, obj=contact)

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
@require_role(Roles.VACANCY_WRITE)
def delete(contact_id):
    """Delete a contact."""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash(_('Contact person deleted.'), 'success')

    return redirect(url_for('contact.list'))
