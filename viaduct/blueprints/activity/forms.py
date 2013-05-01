from flask.ext.wtf import Form, TextField, TextAreaField, FileField, DateTimeField, Required

class CreateForm(Form):
	name				= TextField(u'Activity name', validators=[Required()])
	description = TextAreaField(u'Description')
	start_time  = DateTimeField(u'Start time', format='%Y-%m-%d %H:%M:%S') 
	end_time		= DateTimeField(u'End time', format='%Y-%m-%d %H:%M:%S')
	location    = TextField(u'Location', default="VIA Kamer (A0.10)")
	privacy			= TextField(u'Privacy')
	picture			= FileField(u'Picture')
	venue				= TextField(u'Venue')
