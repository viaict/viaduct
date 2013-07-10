from flask.ext.wtf import Form, Required, TextField, TextAreaField, DateField,\
        SelectField, SubmitField

class ContactForm(Form):
    name = TextField('Naam')
    email = TextField('Email')
    phone_nr = TextField('Telefoon')
    location_id = SelectField('Locatie', coerce=int)
    submit = SubmitField('Opslaan')
