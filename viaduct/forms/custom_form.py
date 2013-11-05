from flask.ext.wtf import Form, TextField, PasswordField, SelectField, FieldList, FormField, SubmitField, Required, Email

class CreateForm(Form):
	name	= TextField(u'Formulier naam')
	max_attendants	= TextField(u'Maximale aantal deelnemers')
	origin	= TextField(u'Who')
	html	= TextField(u'Let the dogs out')
	email = TextField('E-mail', validators=[Required(), Email()])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	student_id = TextField('Student ID', validators=[Required()])
	education_id = SelectField('Education', coerce=int)
	submit = SubmitField('Opslaan')
