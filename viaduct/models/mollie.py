from viaduct import db

class Transaction(db.Model):
	__tablename__ = 'mollie_transaction'

	id = db.Column(db.Integer, primary_key=True)
	amount = db.Column(db.Float)
	description = db.Column(db.String(256))
	status = db.Column(db.Enum('open','cancelled', 'paidout', 'paid', 'expired'))
	createdDatetime = db.Column(db.DateTime)
	paidDatetime = db.Column(db.DateTime)
	expiredDatetime = db.Column(db.DateTime)

	# method can be
	#	None
	#	ideal
	#	creditcard
	#	mistercash
	#	paysafecard
	method = db.Column(db.String(256))

	user = db.relationship('User', backref=db.backref('mollie_transaction', lazy='dynamic'))

	def __init__(self, amount=0.0, description="some via Mollie Transaction",
				status='open', createdDatetime=None, paidDatetime=None,
				expiredDatetime=None):
		self.amount = amount
		self.description = description
		self.status = status
		self.createdDatetime = createdDatetime
		self.paidDatetime = paidDatetime
		self.expiredDatetime = expiredDatetime
