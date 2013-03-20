from flask.ext.wtf import FileField, Form, Regexp, Required, SubmitField, \
	TextField

class UploadForm(Form):
	filename = TextField('Name', [Required(), Regexp('^[A-Za-z0-9-]+(.[a-z]+)?$')])
	upload = FileField('File')
	upload_file = SubmitField('Upload File')

