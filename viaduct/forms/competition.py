from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired


class EditTeamForm(Form):
    name = StringField('Naam', validators=[
        InputRequired(message='Geen naam opgegeven')])
