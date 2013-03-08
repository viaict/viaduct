from flask.ext.wtf import Form, BooleanField, TextField, TextAreaField
from flask.ext.wtf import SelectField, SubmitField
from flask.ext.wtf import Optional, NumberRange, Required, Regexp

class EditPageForm(Form):
	title = TextField('Title', [Required()])
	content_type = SelectField('Content Type')
	content = TextAreaField('Content', [Optional()])
	priority = TextField('Priority', [NumberRange()])
	save_page = SubmitField('Save Page')


class ChangePathForm(Form):
	path = TextField('Path', [Required(), Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$', message='You suck at typing URL paths')])
	move_only_this = SubmitField('Only this page')
	move_children = SubmitField('This and its children ')

