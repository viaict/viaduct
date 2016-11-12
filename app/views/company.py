from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort
from flask_babel import lazy_gettext as _
import json

from sqlalchemy import or_, and_

from datetime import datetime

from app import app, db
from app.models.company import Company
from app.models.location import Location
from app.models.contact import Contact
from app.forms import CompanyForm, NewCompanyForm
from app.utils.forms import flash_form_errors
from app.utils.module import ModuleAPI
from app.utils.file import file_upload


blueprint = Blueprint('company', __name__, url_prefix='/companies')

FILE_FOLDER = app.config['FILE_DIR']


@blueprint.route('/get_companies/', methods=['GET'])
def get_companies():
    if not ModuleAPI.can_read('company'):
        return abort(403)

    if not ModuleAPI.can_write('company'):
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
                "logo": company.logo_path,
                "view": url_for('company.view', company_id=company.id),
                "contact": {
                    "email": company.contact.email,
                    "phone_nr": company.contact.phone_nr
                },
                "can_write": ModuleAPI.can_write('company'),
                "edit": url_for('company.edit', company_id=company.id),
                "remove": url_for('company.delete', company_id=company.id),
            })
    return json.dumps({"data": company_list})


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page>/', methods=['GET', 'POST'])
def list(page=1):
    if not ModuleAPI.can_read('company'):
        return abort(403)

    if request.args.get('search') is not None:
        search = request.args.get('search')

        companies = Company.query.join(Location)\
            .filter(or_(Company.name.like('%' + search + '%'),
                        Location.city.like('%' + search + '%')))\
            .order_by(Company.name).order_by(Company.rank)

        if not ModuleAPI.can_write('company'):
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
                               search=search, path=FILE_FOLDER)

    if not ModuleAPI.can_write('company'):
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

    return render_template('company/list.htm', companies=companies, search="",
                           path=FILE_FOLDER)


@blueprint.route('/view/', methods=['GET'])
@blueprint.route('/view/<int:company_id>/', methods=['GET'])
def view(company_id=None):
    """View a company."""
    if not ModuleAPI.can_read('company'):
        return abort(403)

    company = Company.query.get_or_404(company_id)
    return render_template('company/view.htm', company=company,
                           path=FILE_FOLDER)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:company_id>/', methods=['GET', 'POST'])
def edit(company_id=None):
    """Create, view or edit a company."""
    if not ModuleAPI.can_read('company'):
        return abort(403)

    # Select company.
    if company_id:
        company = Company.query.get(company_id)
    else:
        company = Company()

    form = CompanyForm(request.form, company)

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
            logo = file_upload(request.files['file'])
            if logo is not None:
                company.logo_path = logo.name

        db.session.add(company)
        db.session.commit()
        flash(_('Company "%s" saved.' % company.name), 'success')
        return redirect(url_for('company.view', company_id=company.id))
    else:
        flash_form_errors(form)

    return render_template('company/edit.htm', company=company, form=form)


@blueprint.route('/delete/<int:company_id>/', methods=['GET', 'POST'])
def delete(company_id):
    """Delete a company."""
    if not ModuleAPI.can_write('company'):
        return abort(403)

    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash(_('Company "%s" deleted' % company.name), 'success')
    return redirect(url_for('company.list'))


@blueprint.route('/create_new/', methods=['GET', 'POST'])
@blueprint.route('/edit_new/<int:company_id>/', methods=['GET', 'POST'])
def create(company_id=None):
    if not ModuleAPI.can_write('company'):
        return abort(403)

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
    data["file"] = company.logo_path
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
            logo = file_upload(request.files['file'])
            if logo is not None:
                company.logo_path = logo.name

        db.session.add(company)
        db.session.commit()
        flash(_('Company "%s" saved.' % company.name), 'success')
        return redirect(url_for('company.view', company_id=company.id))
    else:
        flash_form_errors(form)

    return render_template('company/create.htm', company=company, form=form)
