from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Email

from flask_babel import lazy_gettext as _


class ContactForm(Form):
    name = StringField(_('Name'), validators=[InputRequired(
        message=_("Name is required."))])
    email = StringField(_('Email'), validators=[InputRequired(
        message=_("Email is required.")), Email(
        message=_("Not a valid email."))])
    phone_nr = StringField(_('Phone'), validators=[InputRequired(
        message=_("Phone is required."))])
    location_id = SelectField('Locatie', coerce=int, validators=[InputRequired(
        message=_('Location is required.'))])
