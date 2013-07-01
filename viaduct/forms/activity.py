from flask.ext.wtf import Form, TextField, TextAreaField, FileField, Required

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
