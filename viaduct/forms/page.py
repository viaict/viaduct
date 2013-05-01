from flask.ext.wtf import Form, BooleanField, TextField, TextAreaField
from flask.ext.wtf import SelectField, SubmitField
from flask.ext.wtf import Optional, NumberRange, Required, Regexp

class EditPageForm(Form):
	title = TextField('Title', [Required()])
	content = TextAreaField('Content', [Optional()])
	comment = TextField('Comment', [Required()])
	filter_html = BooleanField('Disable HTML filtering for the current page.')
	save_page = SubmitField('Save Page')

class ChangePathForm(Form):
	path = TextField('Path', [Required(), Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$', message='You suck at typing URL paths')])
	move_only_this = SubmitField('Only this page')
	move_children = SubmitField('This and its children ')

