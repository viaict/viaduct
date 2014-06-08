from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, \
    DateField, SelectField
from wtforms.validators import InputRequired


class VacancyForm(Form):
    title = StringField('Titel', validators=[InputRequired()])
    description = TextAreaField('Beschrijving', validators=[InputRequired()])
    start_date = DateField('Begindatum', validators=[InputRequired()])
    end_date = DateField('Einddatum', validators=[InputRequired()])
    contract_of_service = SelectField('Contract',
                                      choices=[('voltijd', 'Voltijd'),
                                               ('deeltijd', 'Deeltijd'),
                                               ('bijbaan', 'Bijbaan'),
                                               ('stage', 'Stage')])
    workload = StringField('Werklast', validators=[InputRequired()])
    company_id = SelectField('Bedrijf', coerce=int)
    submit = SubmitField('Opslaan')
