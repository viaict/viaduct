from flask.ext.wtf import Form, TextField, Required, BooleanField, \
		SubmitField, TextAreaField, DateField, SelectField

class VacancyForm(Form):
	title = TextField('Titel', validators=[Required()])
	description = TextAreaField('Beschrijving', validators=[Required()])
	start_date = DateField('Begindatum')
	end_date = DateField('Einddatum')
	contract_of_service = SelectField('Contract', choices=[
			('voltijd', 'Voltijd'), ('deeltijd', 'Deeltijd'),
			('bijbaan', 'Bijbaan'), ('stage', 'Stage')])
	workload = TextField('Werklast')
	company_id = SelectField('Bedrijf', coerce=int)
	submit = SubmitField('Opslaan')