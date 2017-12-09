from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Email

from flask_babel import lazy_gettext as _


class LocationForm(FlaskForm):
    city = StringField(_('City'), validators=[InputRequired()])
    country = StringField(_('Country'), validators=[InputRequired()])
    address = StringField(_('Address'), validators=[InputRequired()])
    zip = StringField(_('Zip code'), validators=[InputRequired()])
    postoffice_box = StringField('Postbus')
    email = StringField(_('Email'), validators=[InputRequired(),
                                                Email(message=_("Not a valid"
                                                                "email."))])
    phone_nr = StringField(_('Phone'), validators=[InputRequired()])
