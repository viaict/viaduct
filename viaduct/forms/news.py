from wtforms import TextAreaField, DateField
from wtforms.validators import InputRequired

from datetime import date, timedelta

from viaduct.forms.page import SuperPageForm


class NewsForm(SuperPageForm):
    content = TextAreaField('Inhoud', validators=[InputRequired()])
    end_time = DateField('Archiefdatum', validators=[InputRequired()],
                         default=date.today() + timedelta(days=1))
