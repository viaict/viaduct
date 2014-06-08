from flask_wtf import Form
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import InputRequired, Regexp


class UploadForm(Form):
    filename = StringField('Name', [InputRequired(),
                                    Regexp('^[A-Za-z0-9-]+(.[a-z]+)?$')])
    upload = FileField('File')
    upload_file = SubmitField('Upload File')
