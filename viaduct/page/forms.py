from flask.ext.wtf import Form, TextField, SubmitField
from flask.ext.wtf import Required, Regexp

class ChangePathForm(Form):
	path = TextField('Path', [Required(), Regexp(r'^ */?[\w-]+(/[\w-]+)*/? *$', message='You suck at typing URL paths')])
	move_only_this = SubmitField('Only this page')
	move_children = SubmitField('This and its children ')

