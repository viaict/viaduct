from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField


class ContactForm(Form):
    name = StringField('Naam')
    email = StringField('Email')
    phone_nr = StringField('Telefoon')
    location_id = SelectField('Locatie', coerce=int)
    submit = SubmitField('Opslaan')
