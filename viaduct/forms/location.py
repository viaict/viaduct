from flask_wtf import Form
from wtforms import StringField, SubmitField


class LocationForm(Form):
    city = StringField('Plaats')
    country = StringField('Land')
    address = StringField('Adres')
    zip = StringField('Postcode')
    postoffice_box = StringField('Postbus')
    email = StringField('Email')
    phone_nr = StringField('Telefoon')
    submit = SubmitField('Opslaan')
