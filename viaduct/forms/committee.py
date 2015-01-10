# coding: utf-8

from viaduct.forms.page import SuperPageForm
from wtforms import TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired


class CommitteeForm(SuperPageForm):
    description = TextAreaField(u'Beschrijving', [InputRequired()])
    group_id = SelectField(u'Groep', coerce=int)
    coordinator_id = SelectField(u'Coördinator', coerce=int)
    interim = BooleanField(u'Interim coördinator')
