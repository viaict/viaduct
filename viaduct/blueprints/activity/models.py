from viaduct import db

class Activity(db.Model):
	__tablename__ = 'activity'

	id          = db.Column(db.Integer, primary_key=True)
	title       = db.Column(db.String(256))
	description = db.Column(db.String(2048))


	def __init__(self, title, description):
		self.title = title
		self.description = description

