from flask.ext.wtf import Form, TextAreaField, FileField, TextField, PasswordField, SelectField, FieldList, FormField, SubmitField, Required, Email

class CreateForm(Form):
	name				= TextField(u'Activity name', validators=[Required()])
	description	= TextAreaField(u'Description', validators=[Required()])
	start_date	= TextField(u'start_time', validators=[Required()]) 
	start_time	= TextField(u'start_time', validators=[Required()]) 
	end_date		= TextField(u'Venue')
	end_time		= TextField(u'Venue')
	location		= TextField(u'Location', default="VIA Kamer (A0.10)")
	privacy			= TextField(u'Privacy')
	price				= TextField(u'Price')
	picture			= FileField(u'Picture')
	venue				= TextField(u'Venue')
	form_id			= SelectField('Formulier', coerce=int)

class ActivityForm(Form):
	email = TextField(u'E-mail address', validators=[Required(), Email()])
	first_name = TextField(u'First name', validators=[Required()])
	last_name = TextField(u'Last name', validators=[Required()])
	student_id = TextField(u'Student ID', validators=[Required()])
	education_id = SelectField(u'Education', coerce=int)
