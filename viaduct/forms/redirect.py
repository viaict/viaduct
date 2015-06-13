from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class RedirectForm(Form):
    fro = StringField(
        'Van', validators=[InputRequired(message='Van pad vereist')])
    to = StringField(
        'Naar', validators=[InputRequired(message='Naar pad vereist')])

    submit = SubmitField('Opslaan')
