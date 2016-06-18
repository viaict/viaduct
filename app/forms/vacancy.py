from flask_wtf import Form
from flask.ext.babel import lazy_gettext as _  # noqa
from wtforms import StringField, SubmitField, TextAreaField, \
    DateField, SelectField
from wtforms.validators import InputRequired


class VacancyForm(Form):
    title = StringField(_('Title'), validators=[InputRequired(
        message=_('A title is required.'))])
    description = TextAreaField(_('Description'), validators=[InputRequired(
        message=_('A description is required.'))])
    start_date = DateField(_('Start date'), validators=[InputRequired(
        message=_('Start date is required.'))])
    end_date = DateField(_('End date'), validators=[InputRequired(
        message=_('End date is required.'))])
    contract_of_service = SelectField(_('Contract'),
                                      choices=[('voltijd', _('Voltijd')),
                                               ('deeltijd', _('Deeltijd')),
                                               ('bijbaan', _('Bijbaan')),
                                               ('stage', _('Stage'))])
    workload = StringField(_('Workload'), validators=[InputRequired(
        message=_('Workload is required.'))])
    company_id = SelectField(_('Company'), coerce=int)
    submit = SubmitField(_('Submit'))
