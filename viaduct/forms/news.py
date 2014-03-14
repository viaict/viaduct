from flask.ext.wtf import TextAreaField, DateField, Required
from datetime import date, timedelta

from viaduct.forms.page import SuperPageForm


class NewsForm(SuperPageForm):
    content = TextAreaField(u'Inhoud', validators=[Required()])
    end_time = DateField(u'Archiefdatum', validators=[Required()],
                         default=date.today() + timedelta(days=1))
