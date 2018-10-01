from flask_wtf import FlaskForm
from flask_babel import _  # gettext

from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.service import user_service


class ChallengeForm(FlaskForm):
    name = StringField('Naam', validators=[InputRequired()])
    description = TextAreaField('Beschrijving', validators=[InputRequired()])
    hint = StringField('Hint')
    start_date = DateField('Begindatum', validators=[InputRequired()])
    end_date = DateField('Einddatum', validators=[InputRequired()])
    weight = StringField('Weging', validators=[InputRequired()])
    answer = StringField('Antwoord', validators=[InputRequired()])


class ManualSubmissionForm(FlaskForm):
    user = QuerySelectField(
        _('User'),
        query_factory=lambda: user_service.find_members())
