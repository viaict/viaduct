from viaduct import db

class ProgrammingLanguage(db.Model):
	__tablename__ = 'programming_language'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256))

	def __init__(self, title):
		self.title = title