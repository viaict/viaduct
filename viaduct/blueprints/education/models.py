from application import db

class education(db.Model):
	__tablename__ = 'education'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256), unique=True)
	description = db.Column(db.String(1024))
	type = db.Column(db.String(256)) # Moet ENUM worden (BSc, 1jarig MSc, 2 jarig MSc)

	def __init__(self, title, description, type):
		self.title = title
		self.description = description
		self.type = type