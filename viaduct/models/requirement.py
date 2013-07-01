from viaduct import db

class Requirement(db.Model):
	__tablename__ = 'requirements'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256), unique=True)
	description = db.Column(db.String(1024))

	def __init__(self, title, description):
		self.title = title
		self.description = description