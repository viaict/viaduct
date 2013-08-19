from flask.ext.wtf import Form, TextField, PasswordField, SelectField, FieldList, FormField, SubmitField, Required, Email

# Who let the dogs out... otherwise the form parser gives an error
class CreateForm(Form):
	#name	= TextField(u'Formulier naam')
	#origin	= TextField(u'Who')
	#html	= TextField(u'Let the dogs out')
	email = TextField('E-mail address', validators=[Required(), Email()])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	student_id = TextField('Student ID', validators=[Required()])
	education_id = SelectField('Education', coerce=int)
	submit = SubmitField('Opslaan')
