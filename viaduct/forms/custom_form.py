from flask.ext.wtf import Form, TextField, PasswordField, SelectField, FieldList, FormField, SubmitField, Required, Email, DecimalField

class CreateForm(Form):
	name	= TextField(u'Formulier naam')
	max_attendants	= TextField(u'Maximale aantal deelnemers')
	msg_success	= TextField(u'Succes bericht : Wordt getoond wanneer gebruiker zich inschrijft')
	origin	= TextField(u'Who')
	html	= TextField(u'Let the dogs out')
	email = TextField('E-mail', validators=[Required(), Email()])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	student_id = TextField('Student ID', validators=[Required()])
	price = DecimalField('Price', places=2, validators=[Required()])
	education_id = SelectField('Education', coerce=int)
	submit = SubmitField('Opslaan')
	transaction_description = TextField('Beschrijving van de transactie')
