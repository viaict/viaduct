from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired


class EditSponsorForm(Form):
    """
    Form used to create and edit sponsors
    """
    name = StringField(
            'Naam', validators=[InputRequired(message='Geen naam opgegeven')])
