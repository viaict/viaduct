from flask.ext.wtf import Form, TextField, Required, BooleanField, \
		SubmitField, TextAreaField, DateField, SelectField

class VacancyForm(Form):
	title = TextField('Titel', validators=[Required()])
	description = TextAreaField('Beschrijving', validators=[Required()])
	start_date = DateField('Begindatum', validators=[Required()])
	end_date = DateField('Einddatum', validators=[Required()])
	contract_of_service = SelectField('Contract', choices=[
			('voltijd', 'Voltijd'), ('deeltijd', 'Deeltijd'),
			('bijbaan', 'Bijbaan'), ('stage', 'Stage')])
	workload = TextField('Werklast', validators=[Required()])
	company_id = SelectField('Bedrijf', coerce=int)
	submit = SubmitField('Opslaan')