from app.forms.fields import EmailField

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired

from flask_babel import lazy_gettext as _


class ContactForm(FlaskForm):
    name = StringField(_('Name'), validators=[InputRequired()])
    email = EmailField(_('Email'), validators=[InputRequired()])
    phone_nr = StringField(_('Phone'), validators=[InputRequired()])
    location_id = SelectField(_('Location'), coerce=int,
                              validators=[InputRequired()])
