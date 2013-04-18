from application import db


class Location(db.Model):
	__tablename__ = 'location'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), unique=True)
	phone_nr = db.Column(db.String(64))
	city = db.Column(db.String(256))
	street = db.Column(db.String(256))
	street_nr = db.Column(db.String(32))
	zip = db.Column(db.String(32))
	postoffice_box = db.Column(db.String(32))
  	
	
	def __init__(self, email, phone_nr, city, street, street_nr, zip, postoffice_box):
		self.email = email
		self.phone_nr = phone_nr
		self.contract_start_date = contract_start_date
		self.contract_end_date = contract_end_date
		self.headquarter_location_id = headquarter_location_id
		self.contact_id = contact_id