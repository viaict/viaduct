from flask.ext.wtf import Form, TextField, TextAreaField, FileField, DateTimeField, Required, validators, IntegerField, SelectField

from models import Minute, Task

class AddTaskForm(Form):
	name				= TextField('Name', validators=[Required()])
	content = TextAreaField('Content', validators=[validators.optional()]) #, validators.length(max=1200)])
	deadline = DateTimeField('Deadline', format='%Y-%m-%d %H:%M:%S')
	# timestamp
	line = IntegerField('Line', default=-1, description='Fill in -1 if this is unknown or impossible.')
	minute_id = IntegerField('Minute ID', default=-1, description='Fill in -1 if this is unknown or impossible.')
	group = SelectField('Group')
	users = TextAreaField('Users', description='Type comma separated names for whom this task is, in a similar manner as you are familiar with whilst taking minutes.', validators=[Required()])
	status = SelectField('Status', choices=map(lambda x, y: (x, y), range(0, len(Task.status_meanings)), Task.status_meanings), validators=[])

	def load_groups(self, groups):
		#self.group.choices = map(lambda x: ("%s%d" % (x.name, x.id), x.name), groups)
		self.group.choices = map(lambda x: (x.id, x.name), groups)


class AddMinuteForm(Form):
	name				= TextField('name', validators=[Required()])
