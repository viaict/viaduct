# coding: utf-8

from viaduct.forms.page import SuperPageForm
from wtforms import TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired


class CommitteeForm(SuperPageForm):
    description = TextAreaField('Beschrijving', [InputRequired()])
    group_id = SelectField('Groep', coerce=int)
    coordinator_id = SelectField('Coördinator', coerce=int)
    interim = BooleanField('Interim coördinator')
