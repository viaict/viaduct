from flask_wtf import Form
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from datetime import date, timedelta


class NewsForm(Form):
    title = StringField(u'Titel', validators=[InputRequired()])
    content = TextAreaField(u'Inhoud', validators=[InputRequired()])
    end_time = DateField(u'Archiefdatum', validators=[InputRequired()],
                         default=date.today() + timedelta(days=1))
