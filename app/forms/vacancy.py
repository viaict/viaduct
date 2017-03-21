from flask_wtf import Form
from flask_babel import lazy_gettext as _  # noqa
from wtforms import StringField, SubmitField, TextAreaField, \
    DateField, SelectField
from wtforms.validators import InputRequired


class VacancyForm(Form):
    title = StringField(_('Title'), validators=[InputRequired()])
    description = TextAreaField(_('Description'), validators=[InputRequired()])
    start_date = DateField(_('Start date'), validators=[InputRequired()])
    end_date = DateField(_('End date'), validators=[InputRequired()])
    contract_of_service = SelectField(_('Contract'),
                                      choices=[('voltijd', _('Voltijd')),
                                               ('deeltijd', _('Deeltijd')),
                                               ('bijbaan', _('Bijbaan')),
                                               ('stage', _('Stage'))])
    workload = StringField(_('Workload'))
    company_id = SelectField(_('Company'), coerce=int)
    submit = SubmitField(_('Submit'))
