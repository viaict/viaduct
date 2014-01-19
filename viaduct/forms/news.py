from flask.ext.wtf import Form, TextField, TextAreaField, DateField, Required
from datetime import date, timedelta


class NewsForm(Form):
    title = TextField(u'Titel', validators=[Required()])
    content = TextAreaField(u'Inhoud', validators=[Required()])
    end_time = DateField(u'Archiefdatum', validators=[Required()],
                         default=date.today() + timedelta(days=1))
