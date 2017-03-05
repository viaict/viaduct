from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Email

from flask_babel import lazy_gettext as _


class ContactForm(Form):
    name = StringField(_('Name'), validators=[InputRequired()])
    email = StringField(_('Email'), validators=[InputRequired(), Email()])
    phone_nr = StringField(_('Phone'), validators=[InputRequired()])
    location_id = SelectField(_('Location'), coerce=int,
                              validators=[InputRequired()])
