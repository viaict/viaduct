from flask_babel import lazy_gettext as _
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired

import app.service.user_service as user_service
from app.forms.fields import DecimalField, EmailField
from app.service import custom_form_service


class CreateForm(FlaskForm):
    name = StringField(_('Form name'), validators=[InputRequired()])
    group = QuerySelectField(
        _('Owner group '),
        query_factory=lambda:
        custom_form_service.get_available_owner_groups_for_user(current_user),
        get_pk=lambda group: group.id,
        get_label=lambda group: group.name)
    max_attendants = StringField(_('Max number of attendants'))
    introductions = SelectField(_('Number of extra attendants allowed'),
                                choices=[(0, _('None'))] +
                                [(x, "+%d" % x) for x in range(1, 11)],
                                default=(0, _('None')))
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


class AddRegistrationForm(FlaskForm):
    user_id = QuerySelectField(
        label='Lid selecteren',
        query_factory=lambda: user_service.find_members(),
        get_pk=lambda user: user.id,
        get_label=lambda user: user.name)
