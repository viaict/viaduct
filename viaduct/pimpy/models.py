from viaduct import db
import datetime

# many to many relationship tables
task_group = db.Table('pimpy_task_group',
	db.Column('task_id', db.Integer, db.ForeignKey('pimpy_task.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

task_user = db.Table('pimpy_task_user',
	db.Column('task_id', db.Integer, db.ForeignKey('pimpy_task.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class ListItem(object):
    name = "jaja"

class Task(ListItem, db.Model):
	__tablename__ = 'pimpy_task'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)
	deadline = db.Column(db.DateTime)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	group_id = db.Column(db.Integer)
	line = db.Column(db.Integer)


	users = db.relationship('User', secondary=task_user,
		backref=db.backref('tasks', lazy='dynamic'), lazy='dynamic')

	#minute_id = db.Column(db.Integer, db.ForeignKey('pimpy_minute.id'))
	minute = db.relationship("Minute", backref='tasks', lazy='dynamic')

	def __init__(self, title, content, deadline, group_id, users,
				minute, line):
		self.title = title
		self.content = content
		self.deadline = deadline
		self.group_id = group_id
		self.line = line

		# TODO: the relationship might need to be set differently?
		self.users = users
		self.minute = minute

class Minute(ListItem, db.Model):
	__tablename__ = 'pimpy_minute'

	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	content = db.Column(db.Text)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

	group = db.relationship('Group', backref='minutes')

	task_id = db.Column(db.Integer, db.ForeignKey('pimpy_task.id'))

	#tasks = db.relationship('pimpy_task', backref='minute', lazy='dynamic')
