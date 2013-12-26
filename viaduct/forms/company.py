from flask.ext.wtf import Form, Required, TextField, TextAreaField, DateField,\
		SelectField, SubmitField, FileField

class CompanyForm(Form):
	name = TextField('Naam', validators=[Required()])
	description = TextAreaField('Beschrijving', validators=[Required()])
	contract_start_date = DateField('Contract begindatum',
			validators=[Required()])
	contract_end_date = DateField('Contract einddatum', validators=[Required()])
	location_id = SelectField('Locatie', coerce=int)
	file = FileField('Logo')
	contact_id = SelectField('Contactpersoon', coerce=int)
	website = TextField('Website')
	submit = SubmitField('Opslaan')