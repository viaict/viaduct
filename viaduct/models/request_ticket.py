from viaduct import db
import datetime

class Password_ticket(db.Model):
	__tablename__ = 'password_ticket'

	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.Integer, db.ForeignKey('user.id'),
		nullable=False)
	created_on = db.Column(db.DateTime, nullable=False)
	hash = db.Column(db.String(64), nullable=False)

	def __init__(self, user_id=None, hash=None):
		self.created_on = datetime.datetime.now()
		self.user = user_id
		self.hash = hash