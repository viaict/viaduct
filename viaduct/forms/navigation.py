from flask.ext.wtf import Form, TextField, Required, BooleanField, SubmitField

class NavigationEntryForm(Form):
	title = TextField('Titel', validators=[Required()])
	url = TextField('URL', validators=[Required()])
	external = BooleanField('Externe link', default=False)
	activity_list = BooleanField('Lijst van activiteiten', default=False)
	submit = SubmitField('Opslaan')
