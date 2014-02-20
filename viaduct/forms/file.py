from flask.ext.wtf import Form, FileField, SubmitField


class FileForm(Form):
    file = FileField('Bestand')
    submit = SubmitField('Uploaden')
