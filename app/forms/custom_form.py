from flask_wtf import Form
from flask_babel import lazy_gettext as _
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired, Email
from app.forms.fields import DecimalField


class CreateForm(Form):
    name = StringField(_('Form name'), validators=[InputRequired()])
    max_attendants = StringField(_('Max number of attendents'))
    msg_success = StringField(
        _('Success message: shown when user registers'))
    origin = StringField(_('Who'))
    html = StringField(_('Let the dogs out'))
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    first_name = StringField('Voornaam', validators=[InputRequired()])
    last_name = StringField('Achternaam', validators=[InputRequired()])
    student_id = StringField('Student ID', validators=[InputRequired()])
    price = DecimalField(_('Price'), places=2, validators=[InputRequired()])
    education_id = SelectField('Opleiding', coerce=int)
    terms = StringField(_('Conditions'))
