from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class RedirectForm(FlaskForm):
    fro = StringField(
        'Van', validators=[InputRequired(message='Van pad vereist')])
    to = StringField(
        'Naar', validators=[InputRequired(message='Naar pad vereist')])

    submit = SubmitField('Opslaan')
