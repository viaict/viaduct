import json
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort
from flask_babel import lazy_gettext as _
from flask_login import current_user
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename

from app import db
from app.decorators import require_role
from app.forms.company import CompanyForm, NewCompanyForm
from app.models.company import Company
from app.models.contact import Contact
from app.models.location import Location
from app.roles import Roles
from app.service import role_service, file_service
from app.utils.forms import flash_form_errors
from app.enums import FileCategory

blueprint = Blueprint('company', __name__, url_prefix='/companies')


@blueprint.route('/get_companies/', methods=['GET'])
def get_companies():
    vacancy_write = role_service.user_has_role(current_user,
                                               Roles.VACANCY_WRITE)
    if not vacancy_write:
        companies = Company.query\
            .filter(and_(Company.contract_start_date < datetime.utcnow(),
                         Company.contract_end_date > datetime.utcnow()))\
            .order_by(Company.name).order_by(Company.rank).all()
        for company in companies:
            company.expired = False
    else:
        companies = Company.query.filter().order_by(Company.name)\
            .order_by(Company.rank).all()
        for company in companies:
            if company.contract_start_date < datetime.date(datetime.utcnow()) \
                    and company.contract_end_date < datetime.date(datetime
                                                                  .utcnow()):
                company.expired = True
            else:
                company.expired = False

    company_list = []

    for company in companies:
        company_list.append(
            {
                "id": company.id,
                "name": company.name,
                "website": company.website,
                "description": company.description,
                "location": {
                    "city": company.location.city,
                    "address": company.location.address,
                    "country": company.location.country
                },
                "expired": company.expired,
                "logo": url_for('company.view_logo', company_id=company.id),
                "view": url_for('company.view', company_id=company.id),
                "contact": {
                    "email": company.contact.email,
                    "phone_nr": company.contact.phone_nr
                },
                "can_write": vacancy_write,
                "edit": url_for('company.edit', company_id=company.id),
                "remove": url_for('company.delete', company_id=company.id),
            })
    return json.dumps({"data": company_list})


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
    if request.args.get('search') is not None:
        search = request.args.get('search')

        companies = Company.query.join(Location)\
            .filter(or_(Company.name.like('%' + search + '%'),
                        Location.city.like('%' + search + '%')))\
            .order_by(Company.name).order_by(Company.rank)

        if not role_service.user_has_role(current_user, Roles.VACANCY_WRITE):
            companies = companies\
                .filter(and_(Company.contract_start_date < datetime.utcnow(),
                             Company.contract_end_date > datetime.utcnow()))\
                .paginate(page, 15, True)
        else:
            for i, company in enumerate(companies):
                print((i, company))
                if company.contract_start_date < datetime\
                        .date(datetime.utcnow()) and \
                        company.contract_end_date < datetime\
                        .date(datetime.utcnow()):
                    companies[i].expired = True
            companies = companies.paginate(page, 15, False)

        return render_template('company/list.htm', companies=companies,
                               search=search)

    if not role_service.user_has_role(current_user, Roles.VACANCY_WRITE):
        companies = Company.query\
            .filter(and_(Company.contract_start_date < datetime.utcnow(),
                         Company.contract_end_date > datetime.utcnow()))\
            .order_by(Company.name).order_by(Company.rank).paginate(page, 15,
                                                                    True)
    else:
        companies = Company.query.filter().order_by(Company.name)\
            .order_by(Company.rank)
        for i, company in enumerate(companies):
            if company.contract_start_date < datetime.date(datetime.utcnow()) \
                    and company.contract_end_date < datetime.date(datetime
                                                                  .utcnow()):
                companies[i].expired = True
        companies = companies.paginate(page, 15, False)
        # todo fix message if inactive

    # companies = Company.query.paginate(page, 15, False)

    return render_template('company/list.htm', companies=companies, search="")


@blueprint.route('/view/<int:company_id>/', methods=['GET'])
def view(company_id=None):
    """View a company."""

    company = Company.query.get_or_404(company_id)
    can_write = role_service.user_has_role(current_user, Roles.VACANCY_WRITE)
    return render_template('company/view.htm', company=company,
                           can_write=can_write)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:company_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def edit(company_id=None):
    """Create, view or edit a company."""
    # Select company.
    if company_id:
        company = Company.query.get(company_id)
    else:
        company = Company()

    form = CompanyForm(request.form, obj=company)

    # Add locations.
    locations = Location.query.order_by('address').order_by('city')
    form.location_id.choices = \
        [(l.id, l.address + ', ' + l.city) for l in locations]

    form.contact_id.choices = \
        [(c.id, c.name) for c in Contact.query.filter_by().order_by('name')]

    if form.validate_on_submit():
        if not company.id and Company.query.filter(
                Company.name == form.name.data).count():
            flash(_('Name "%s" is already in use.' % form.name.data),
                  'danger')
            return render_template('company/edit.htm', company=company,
                                   form=form)
        company.name = form.name.data
        company.description = form.description.data
        company.contract_start_date = form.contract_start_date.data
        company.contract_end_date = form.contract_end_date.data
        company.location = Location.query.get(form.location_id.data)
        company.contact = Contact.query.get(form.contact_id.data)
        company.website = form.website.data
        if request.files['file']:
            logo = request.files['file']
            _file = file_service.add_file(FileCategory.COMPANY_LOGO,
                                          logo, logo.filename)
            company.logo_file_id = _file.id

        db.session.add(company)
        db.session.commit()
        flash(_('Company "%s" saved.' % company.name), 'success')
        return redirect(url_for('company.view', company_id=company.id))

    return render_template('company/edit.htm', company=company, form=form)


@blueprint.route('/delete/<int:company_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def delete(company_id):
    """Delete a company."""
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash(_('Company "%s" deleted' % company.name), 'success')
    return redirect(url_for('company.list'))


@blueprint.route('/create_new/', methods=['GET', 'POST'])
@blueprint.route('/edit_new/<int:company_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def create(company_id=None):
    # Select company.
    if company_id:
        company = Company.query.get_or_404(company_id)
    else:
        company = Company()

    data = {}

    data["name"] = company.name
    data["description"] = company.description
    data["contract_start_date"] = company.contract_start_date
    data["contract_end_date"] = company.contract_end_date
    data["website"] = company.website

    # Select locations.
    if company.location_id:
        location = Location.query.get(company.location_id)
    else:
        location = Location()

    data['location_city'] = location.city
    data['location_country'] = location.country
    data['location_address'] = location.address
    data['location_zip'] = location.zip
    data['location_postoffice_box'] = location.postoffice_box
    data['location_email'] = location.email
    data['location_phone_nr'] = location.phone_nr

    if company.contact_id:
        contact = Contact.query.get(company.contact_id)
    else:
        contact = Contact()

    data['contact_name'] = contact.name
    data['contact_email'] = contact.email
    data['contact_phone_nr'] = contact.phone_nr

    form = NewCompanyForm(request.form, data=data)

    if form.validate_on_submit():

        if not contact.id and Contact.query.filter(
                Contact.name == form.contact_name.data).count():
            flash(_('Contact name "%s" is already in use.' %
                    form.contact_name.data), 'danger')
            return render_template('company/create.htm', company=company,
                                   form=form)
        if not contact.id and Contact.query.filter(
                Contact.email == form.contact_email.data).count():
            flash(_('Contact email "%s" is already in use.' %
                    form.contact_email.data), 'danger')
            return render_template('company/create.htm', company=company,
                                   form=form)
        contact.name = form.contact_name.data
        contact.email = form.contact_email.data
        contact.phone_nr = form.contact_phone_nr.data
        # Create or update to contact
        db.session.add(contact)
        db.session.commit()

        # Create or update to location
        location.city = form.location_city.data
        location.country = form.location_country.data
        location.address = form.location_address.data
        location.zip = form.location_zip.data
        location.postoffice_box = form.location_postoffice_box.data
        location.email = form.location_email.data
        location.phone_nr = form.location_phone_nr.data
        db.session.add(location)
        db.session.commit()

        #
        if not company.id and Company.query.filter(
                Company.name == form.name.data).count():
            flash(_('Name "%s" is already in use.' % form.name.data),
                  'danger')
            return render_template('company/edit.htm', company=company,
                                   form=form)
        company.name = form.name.data
        company.description = form.description.data
        company.contract_start_date = form.contract_start_date.data
        company.contract_end_date = form.contract_end_date.data
        company.location = location
        company.contact = contact
        company.website = form.website.data
        if request.files['file']:
            logo = request.files['file']
            _file = file_service.add_file(FileCategory.COMPANY_LOGO,
                                          logo, logo.filename)
            company.logo_file = _file

        db.session.add(company)
        db.session.commit()
        flash(_('Company "%s" saved.' % company.name), 'success')
        return redirect(url_for('company.view', company_id=company.id))
    else:
        flash_form_errors(form)

    return render_template('company/create.htm', company=company, form=form)


@blueprint.route('/view_logo/<int:company_id>/', methods=['GET'])
def view_logo(company_id):
    company = Company.query.get_or_404(company_id)

    if company.logo_file_id is None:
        return abort(404)

    logo_file = file_service.get_file_by_id(company.logo_file_id)

    mimetype = file_service.get_file_mimetype(logo_file)
    content = file_service.get_file_content(logo_file)

    fn = secure_filename('logo_' + company.name)
    if len(logo_file.extension) > 0:
        fn += "." + logo_file.extension

    headers = {
        'Content-Type': mimetype,
        'Content-Disposition': 'inline; filename="{}"'.format(fn)
    }

    return content, headers
