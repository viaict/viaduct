from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import InputRequired, Email


class CreateForm(Form):
    name = StringField('Formulier naam')
    max_attendants = StringField('Maximale aantal deelnemers')
    msg_success = StringField('Succes bericht : Wordt getoond wanneer' +
                              'gebruiker zich inschrijft')
    origin = StringField('Who')
    html = StringField('Let the dogs out')
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    first_name = StringField('Voornaam', validators=[InputRequired()])
    last_name = StringField('Achternaam', validators=[InputRequired()])
    student_id = StringField('Student ID', validators=[InputRequired()])
    price = DecimalField('Prijs', places=2, validators=[InputRequired()])
    education_id = SelectField('Opleiding', coerce=int)
    submit = SubmitField('Opslaan')
    transaction_description = StringField('Beschrijving van de transactie')
    terms = StringField('Voorwaarden')
