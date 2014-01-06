from viaduct import db

class Transaction(db.Model):
	__tablename__ = 'mollie_transaction'

	id = db.Column(db.Integer, primary_key=True)
	mollie_id = db.Column(db.String(256))
	amount = db.Column(db.Float)
	description = db.Column(db.String(256))
	status = db.Column(db.Enum('open','cancelled', 'paidout', 'paid', 'expired'))
	createdDatetime = db.Column(db.DateTime)
	paidDatetime = db.Column(db.DateTime)
	expiredDatetime = db.Column(db.DateTime)
	cancelledDatetime = db.Column(db.DateTime)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User', backref=db.backref('mollie_transaction', lazy='dynamic'))

	def __init__(self, amount=0.0, description="some via Mollie Transaction",
				status='open', createdDatetime=None, paidDatetime=None,
				expiredDatetime=None, user=None):
		self.amount = amount
		self.description = description
		self.status = status
		self.createdDatetime = createdDatetime
		self.paidDatetime = paidDatetime
		self.expiredDatetime = expiredDatetime
		self.user = user
