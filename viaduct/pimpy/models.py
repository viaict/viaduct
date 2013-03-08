from viaduct import db

# many to many relationship tables
task_group = db.Table('pimpy_task_group',
	db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

task_user = db.Table('pimpy_task_user',
	db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Task(db.Model):
	__tablename__ = 'pimpy_task'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)
	deadline = db.Column(db.DateTime)
	timestamp = db.Column(db.DateTime, default=datetime.now)
	group_id = db.Column(db.Integer)
	line = db.Column(db.Integer)

	users = db.relationship('User', secondary=user_task,
		backref=db.backref('tasks', lazy='dynamic'), lazy='dynamic')
	minute = db.relationship("Minute", backref='Tasks', lazy='dynamic')

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

class Minute(db.Model):
	__tablename__ = 'pimpy_minute'

	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.now)
	content = db.Column(db.Text)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	group = db.relationship('Group', backref='Minutes', lazy='dynamic')
