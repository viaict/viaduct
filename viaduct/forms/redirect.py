from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class RedirectForm(Form):
    fro = StringField(
        'Fro', validators=[InputRequired(message='Fro path required')])
    to = StringField(
        'To', validators=[InputRequired(message='To path required')])

    submit = SubmitField('Save')
