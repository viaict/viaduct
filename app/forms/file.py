from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import SubmitField


class FileForm(Form):
    file = FileField('Bestand')
    submit = SubmitField('Uploaden')
