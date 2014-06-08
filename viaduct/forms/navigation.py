from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import InputRequired


class NavigationEntryForm(Form):
    title = StringField('Titel', validators=[InputRequired()])
    parent_id = StringField('Lijst')
    url = StringField('URL', validators=[InputRequired()])
    external = BooleanField('Externe link', default=False)
    activity_list = BooleanField('Lijst van activiteiten', default=False)
    submit = SubmitField('Opslaan')
