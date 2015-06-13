# coding: utf-8

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired


class CourseForm(Form):
    title = StringField('Titel', validators=[InputRequired(
        message='Geen titel opgegeven.')])
    description = StringField('Omschrijving')


class EducationForm(Form):
    title = StringField('Titel', validators=[InputRequired(
        message='Geen titel opgegeven.')])
