from flask.ext.wtf import Form, Required, TextField, TextAreaField, DateField,\
		SelectField, SubmitField

class LocationForm(Form):
	city = TextField('Plaats')
	country = TextField('Land')
	address = TextField('Adres')
	zip = TextField('Postcode')
	postoffice_box = TextField('Postbus')
	email = TextField('Email')
	phone_nr = TextField('Telefoon')
	submit = SubmitField('Opslaan')
