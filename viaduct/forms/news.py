from wtforms import TextAreaField, DateField
from wtforms.validators import InputRequired

from datetime import date, timedelta

from viaduct.forms.page import SuperPageForm


class NewsForm(SuperPageForm):
    content = TextAreaField(u'Inhoud', validators=[InputRequired()])
    end_time = DateField(u'Archiefdatum', validators=[InputRequired()],
                         default=date.today() + timedelta(days=1))
