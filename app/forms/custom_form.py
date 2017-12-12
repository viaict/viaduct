from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import InputRequired

from app.forms.fields import DecimalField, EmailField


class CreateForm(FlaskForm):
    name = StringField(_('Form name'), validators=[InputRequired()])
    max_attendants = StringField(_('Max number of attendents'))
    msg_success = StringField(
        _('Success message: shown when user registers'))
    origin = StringField(_('Who'))
    html = StringField(_('Let the dogs out'))
    email = EmailField('E-mail', validators=[InputRequired()])
    first_name = StringField('Voornaam', validators=[InputRequired()])
    last_name = StringField('Achternaam', validators=[InputRequired()])
    student_id = StringField('Student ID', validators=[InputRequired()])
    price = DecimalField(_('IDeal price'), places=2,
                         validators=[InputRequired()])
    requires_direct_payment = BooleanField(_('Requires direct payment'),
                                           default=False)
    education_id = SelectField('Opleiding', coerce=int)
    terms = StringField(_('Conditions'))
