from viaduct import db

class ContactInformation(db.Model):
	__tablename__ = 'contact_information'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(256))
	email = db.Column(db.String(256), unique=True)
	phone_nr = db.Column(db.String(64))
	location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

	location = db.relationship('Location',
			backref=db.backref('contact_informations', lazy='dynamic'))
	
	def __init__(self, name, email, phone_nr, location):
		self.name = name
		self.email = email
		self.phone_nr = phone_nr
		self.location = location
