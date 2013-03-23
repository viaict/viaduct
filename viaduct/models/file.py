from viaduct import db

class File(db.Model):
	__tablename__ = 'file'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(256), nullable=False)
	filename = db.Column(db.String(256), nullable=False)

	def __init__(self, name, filename):
		self.name = name
		self.filename = filename

