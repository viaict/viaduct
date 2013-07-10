from flask.ext.wtf import Form, Required, TextField, TextAreaField, DateField,\
		SelectField, SubmitField

class CompanyForm(Form):
	name = TextField('Naam', validators=[Required()])
	description = TextAreaField('Beschrijving', validators=[Required()])
	contract_start_date = DateField('Contract begindatum',
			validators=[Required()])
	contract_end_date = DateField('Contract einddatum', validators=[Required()])
	location_id = SelectField('Locatie', coerce=int)
	contact_id = SelectField('Contactpersoon', coerce=int)
	submit = SubmitField('Opslaan')