from flask_wtf import Form
from wtforms import FileField, SelectField
from wtforms.validators import InputRequired

from viaduct.forms.page import SuperPageForm


class ExaminationForm(SuperPageForm):
    path = FileField(u'Tentamen', validators=[InputRequired()])
    answer_path = FileField(u'Antwoorden')
    course_id = SelectField(u'Vak', coerce=int, validators=[InputRequired()])
    education_id = SelectField(u'Opleiding', coerce=int,
                               validators=[InputRequired()])
