from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, \
    DateField, SelectField
from wtforms.validators import InputRequired


class ChallengeForm(FlaskForm):
    name = StringField('Naam', validators=[InputRequired()])
    description = TextAreaField('Beschrijving', validators=[InputRequired()])
    hint = StringField('Hint', validators=[InputRequired()])
    type = SelectField('Type',
                       choices=[('text', 'Tekst'),
                                ('image', 'Foto'),
                                ('custom', 'Handmatig')])
    start_date = DateField('Begindatum', validators=[InputRequired()])
    end_date = DateField('Einddatum', validators=[InputRequired()])
    weight = StringField('Weging', validators=[InputRequired()])
    answer = StringField('Antwoord', validators=[InputRequired()])
    parent_id = SelectField('Parent', coerce=int)
    submit = SubmitField('Opslaan')
