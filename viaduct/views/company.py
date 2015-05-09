from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort

from sqlalchemy import or_, and_

from datetime import datetime

from viaduct import application, db
from viaduct.models.company import Company
from viaduct.models.location import Location
from viaduct.models.contact import Contact
from viaduct.forms import CompanyForm, NewCompanyForm
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.file import FileAPI


blueprint = Blueprint('company', __name__, url_prefix='/companies')

UPLOAD_FOLDER = application.config['UPLOAD_DIR']
FILE_FOLDER = application.config['FILE_DIR']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page>/', methods=['GET', 'POST'])
def view_list(page=1):
    if not GroupPermissionAPI.can_read('company'):
        return abort(403)

    if request.args.get('search') is not None:
        search = request.args.get('search')

        companies = Company.query.join(Location)\
            .filter(or_(Company.name.like('%' + search + '%'),
                        Location.city.like('%' + search + '%')))\
            .order_by(Company.name).order_by(Company.rank)

        if not GroupPermissionAPI.can_write('company'):
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

    if not GroupPermissionAPI.can_write('company'):
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


@blueprint.route('/create/', methods=['GET'])
@blueprint.route('/edit/<int:company_id>/', methods=['GET'])
def edit(company_id=None):
    '''
    FRONTEND
    Create, view or edit a company.
    '''
    if not GroupPermissionAPI.can_read('company'):
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

    # Add contacts.
    # form.contact_id.choices = \
    #       [(c.id, c.name) for c in Contact.query\
    #               .filter_by(location=location).order_by('name')]
    form.contact_id.choices = \
        [(c.id, c.name) for c in Contact.query.filter_by().order_by('name')]

    return render_template('company/edit.htm', company=company, form=form)


@blueprint.route('/view/', methods=['GET'])
@blueprint.route('/view/<int:company_id>/', methods=['GET'])
def view(company_id=None):
    '''
    FRONTEND
    view a company.
    '''
    if not GroupPermissionAPI.can_read('company'):
        return abort(403)

    # Select company.
    if company_id:
        company = Company.query.get(company_id)
    if company_id is None or not company:
        return redirect(url_for('company.view_list'))

    return render_template('company/view.htm', company=company,
                           path=FILE_FOLDER)


@blueprint.route('/create/', methods=['POST'])
@blueprint.route('/edit/<int:company_id>/', methods=['POST'])
def update(company_id=None):
    # print request.files
    '''
    BACKEND
    Create, view or edit a company.
    '''
    if not GroupPermissionAPI.can_write('company'):
        return abort(403)

    # Select company.
    if company_id:
        company = Company.query.get(company_id)
    else:
        company = Company()

    form = CompanyForm(request.form, company)

    error_found = False
    if not form.name.data:
        flash('Geen titel opgegeven', 'danger')
        error_found = True
    if not form.description.data:
        flash('Geen beschrijving opgegeven', 'danger')
        error_found = True
    if not form.contract_start_date.data:
        flash('Geen contract begindatum opgegeven', 'danger')
        error_found = True
    if not form.contract_end_date.data:
        flash('Geen contract einddatum opgegeven', 'danger')
        error_found = True
    if 'location_id' not in request.form:
        flash('Geen locatie opgegeven', 'danger')
        error_found = True
    if 'contact_id' not in request.form:
        flash('Geen contactpersoon opgegeven', 'danger')
        error_found = True
    if 'website' not in request.form:
        flash('Geen website opgegeven', 'danger')
        error_found = True
    if request.files['file']:
        logo = FileAPI.upload(request.files['file'])
        company.logo_path = logo.name
        print((vars(logo)))
        pass

    if error_found:
        return redirect(url_for('company.view', company_id=company_id))

    company.name = form.name.data
    company.description = form.description.data
    company.contract_start_date = form.contract_start_date.data
    company.contract_end_date = form.contract_end_date.data
    company.location = Location.query.get(form.location_id.data)
    company.contact = Contact.query.get(form.contact_id.data)
    company.website = form.website.data

    db.session.add(company)
    db.session.commit()

    if company_id:
        flash('Bedrijf opgeslagen', 'success')
    else:
        company_id = company.id
        flash('Bedrijf aangemaakt', 'success')

    return redirect(url_for('company.view', company_id=company_id))


@blueprint.route('/delete/<int:company_id>/', methods=['POST'])
def delete(company_id):
    '''
    BACKEND
    Delete a company.
    '''
    print('POST request received')
    if not GroupPermissionAPI.can_write('company'):
        return abort(403)

    company = Company.query.get(company_id)
    if not company:
        return abort(404)

    db.session.delete(company)
    db.session.commit()
    flash('Bedrijf verwijderd', 'success')

    return redirect(url_for('company.list_view'))


@blueprint.route('/create_new/', methods=['GET'])
@blueprint.route('/edit_new/<int:company_id>/', methods=['GET'])
def create(company_id=None):
    if not GroupPermissionAPI.can_read('company'):
        return abort(403)

    # Select company.
    if company_id:
        company = Company.query.get(company_id)
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

    return render_template('company/create.htm', company=company,
                           location=location, contact=contact, form=form)


@blueprint.route('/create_new/', methods=['POST'])
@blueprint.route('/edit_new/<int:company_id>/', methods=['POST'])
def update_new(company_id=None):
    # print request.files
    '''
    BACKEND
    Create, view or edit a company.
    '''
    if not GroupPermissionAPI.can_write('company'):
        return abort(403)

    # Select company.
    if company_id:
        company = Company.query.get(company_id)
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

    form = NewCompanyForm(request.form, data)

    error_found = False
    if not form.name.data:
        flash('Geen titel opgegeven', 'danger')
        error_found = True
    if not form.description.data:
        flash('Geen beschrijving opgegeven', 'danger')
        error_found = True
    if not form.contract_start_date.data:
        flash('Geen contract begindatum opgegeven', 'danger')
        error_found = True
    if not form.contract_end_date.data:
        flash('Geen contract einddatum opgegeven', 'danger')
        error_found = True
    if 'website' not in request.form:
        flash('Geen website opgegeven', 'danger')
        error_found = True
    if 'contact_name' not in request.form:
        flash('Geen contact name opgegeven', 'danger')
        error_found = True
    if 'contact_email' not in request.form:
        flash('Geen contact email opgegeven', 'danger')
        error_found = True
    if 'contact_phone_nr' not in request.form:
        flash('Geen contact phone nr opgegeven', 'danger')
        error_found = True
    if 'location_city' not in request.form:
        flash('Geen location city opgegeven', 'danger')
        error_found = True
    if 'location_country' not in request.form:
        flash('Geen location country opgegeven', 'danger')
        error_found = True
    if 'location_address' not in request.form:
        flash('Geen location address opgegeven', 'danger')
        error_found = True
    if 'location_zip' not in request.form:
        flash('Geen location zip opgegeven', 'danger')
        error_found = True
    if 'location_postoffice_box' not in request.form:
        flash('Geen location postoffice_box opgegeven', 'danger')
        error_found = True
    if 'location_email' not in request.form:
        flash('Geen location email opgegeven', 'danger')
        error_found = True
    if 'location_phone_nr' not in request.form:
        flash('Geen location phone nr opgegeven', 'danger')
        error_found = True
    if request.files['file']:
        logo = FileAPI.upload(request.files['file'])
        if logo is None and data["file"] is None:
            flash('Geen logo opgegeven', 'danger')
            error_found = True
        elif logo is not None:
            company.logo_path = logo.name
        pass

    if error_found:
        return render_template('company/create.htm', company=company,
                               location=location, contact=contact, form=form)

    # Create or update to contact
    contact.name = form.contact_name.data
    contact.email = form.contact_email.data
    contact.phone_nr = form.contact_phone_nr.data

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

    # Create or update to company
    company.name = form.name.data
    company.description = form.description.data
    company.contract_start_date = form.contract_start_date.data
    company.contract_end_date = form.contract_end_date.data
    company.location = location
    company.contact = contact
    company.website = form.website.data

    db.session.add(company)
    db.session.commit()

    if company_id:
        flash('Bedrijf opgeslagen', 'success')
    else:
        company_id = company.id
        flash('Bedrijf aangemaakt', 'success')

    return redirect(url_for('company.view', company_id=company_id))
