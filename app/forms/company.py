from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_babel import lazy_gettext as _
from wtforms import StringField, SelectField, TextAreaField, DateField
from wtforms.validators import InputRequired
from app.forms.util import FieldVerticalSplit


class CompanyForm(FlaskForm):
    name = StringField(_('Name'), validators=[InputRequired()])
    description = TextAreaField('Description')
    contract_start_date = DateField(_('Contract startdate'),
                                    validators=[InputRequired()])
    contract_end_date = DateField(_('Contract enddate'),
                                  validators=[InputRequired()])

    daterange = FieldVerticalSplit(
        [['contract_start_date'], ['contract_end_date']])

    location_id = SelectField(_('Location'), coerce=int)
    file = FileField(_('Logo'))
    contact_id = SelectField(_('Contact person'), coerce=int)
    website = StringField(_('Website'))


class NewCompanyForm(FlaskForm):
    name = StringField(_('Name'), validators=[InputRequired(
        message=_("Name is required."))])
    description = TextAreaField('Description')
    contract_start_date = DateField(
        _('Contract startdate'), validators=[InputRequired(
            message=_("Contract startdate is required."))])
    contract_end_date = DateField(
        _('Contract enddate'), validators=[InputRequired(
            message=_("Contract enddate is required."))])
    file = FileField(_('Logo'))
    website = StringField(_('Website'))
    contact_name = StringField(_('Contact Name'))
    contact_email = StringField(
        _('Contact email'), validators=[InputRequired(
            message=_("Contact email is required."))])
    contact_phone_nr = StringField(_('Contact Phone'))
    location_city = StringField(_('City'))
    location_country = StringField(_('Country'))
    location_address = StringField(_('Address'))
    location_zip = StringField(_('Zip code'))
    location_postoffice_box = StringField(_('Postoffice Box'))
    location_email = StringField(_('Company email'))
    location_phone_nr = StringField(_('Company Phone'))
