from flask_wtf import Form
from wtforms import TextField, TextAreaField, DateField
from wtforms.validators import InputRequired
from flask.ext.babel import _

from datetime import date, timedelta


class NewsForm(Form):
    title = TextField(_('Title'), validators=[InputRequired()])
    content = TextAreaField(_('Content'), validators=[InputRequired()])
    end_time = DateField(_('Archive date'),
                         default=str(date.today() + timedelta(days=31)))
