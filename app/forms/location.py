from app.forms.fields import EmailField

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired

from flask_babel import lazy_gettext as _


class LocationForm(FlaskForm):
    city = StringField(_('City'), validators=[InputRequired()])
    country = StringField(_('Country'), validators=[InputRequired()])
    address = StringField(_('Address'), validators=[InputRequired()])
    zip = StringField(_('Zip code'), validators=[InputRequired()])
    postoffice_box = StringField('Postbus')

    email = EmailField(_('Email'), validators=[InputRequired()])
    phone_nr = StringField(_('Phone'), validators=[InputRequired()])
