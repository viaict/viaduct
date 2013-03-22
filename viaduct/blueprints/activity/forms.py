from flask.ext.wtf import Form, TextField,
from flask.ext.wtf import Required, Email, EqualTo

class CreateForm(Form):
	title = TextField('title', validators=[Required()])
	description = TextField('description')