from application import db

'''
user_group = db.Table('user_group',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)
'''

class Company(db.Model):
	__tablename__ = 'company'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(256), unique=True)
	description = db.Column(db.String(1024))
	contract_start_date = db.Column(db.DateTime(timezone='Europe/Amsterdam')) # weet niet of timezone zo werkt
	contract_end_date = db.Column(db.DateTime(timezone='Europe/Amsterdam'))
	headquarter_location_id = db.Column(db.Integer)
	contact_id = db.Column(db.Integer)
	
	
	def __init__(self, title, description, contract_start_date, contract_end_date, headquarter_location_id, contact_id):
		self.name = name
		self.description = description
		self.contract_start_date = contract_start_date
		self.contract_end_date = contract_end_date
		self.headquarter_location_id = headquarter_location_id
		self.contact_id = contact_id