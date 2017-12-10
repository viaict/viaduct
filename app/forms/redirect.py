from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class RedirectForm(FlaskForm):
    fro = StringField('Van', validators=[InputRequired()])
    to = StringField('Naar', validators=[InputRequired()])

    submit = SubmitField('Opslaan')
