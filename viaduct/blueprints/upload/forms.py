from flask.ext.wtf import Form, FieldList, FileField, SubmitField
from flask.ext.wtf import Required, Regexp

class UploadForm(Form):
	attachments = FieldList(FileField('file'), 'attachments')
	add_attachment = SubmitField('Add attachment')
	upload = SubmitField('Upload')

