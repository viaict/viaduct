from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Email

from flask_babel import lazy_gettext as _


class LocationForm(FlaskForm):
    city = StringField(_('City'), validators=[InputRequired(
        message=_("City is required."))])
    country = StringField(_('Country'), validators=[InputRequired(
        message=_("Country is required."))])
    address = StringField(_('Address'), validators=[InputRequired(
        message=_("Address is required."))])
    zip = StringField(_('Zip code'), validators=[InputRequired(
        message=_("Zip code is required."))])
    postoffice_box = StringField('Postbus')
    email = StringField(_('Email'), validators=[InputRequired(
        message=_("Email is required.")), Email(
        message=_("Not a valid email."))])
    phone_nr = StringField(_('Phone'), validators=[InputRequired(
        message=_("Phone is required."))])
