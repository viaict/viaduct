from application import db

class User(db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), unique=True)
	password = db.Column(db.String(60))
	first_name = db.Column(db.String(256))
	last_name = db.Column(db.String(256))
	page_edits = db.relationship('PageRevision', backref='author',
		lazy='dynamic')

	def __init__(self, email, password, first_name, last_name):
		self.email = email
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
	
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

