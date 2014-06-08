from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField, DateField, \
    SubmitField
from wtforms.validators import InputRequired


class CompanyForm(Form):
    name = StringField('Naam', validators=[InputRequired()])
    description = TextAreaField('Beschrijving', validators=[InputRequired()])
    contract_start_date = DateField('Contract begindatum',
                                    validators=[InputRequired()])
    contract_end_date = DateField('Contract einddatum',
                                  validators=[InputRequired()])
    location_id = SelectField('Locatie', coerce=int)
    file = FileField('Logo')
    contact_id = SelectField('Contactpersoon', coerce=int)
    website = StringField('Website')
    submit = SubmitField('Opslaan')
