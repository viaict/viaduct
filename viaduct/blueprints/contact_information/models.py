from application import db

'''
user_group = db.Table('user_group',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)
'''

class Contact_information(db.Model):
	__tablename__ = 'contact_information'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(256))
	email = db.Column(db.String(256), unique=True)
	phone_nr = db.Column(db.String(64))
	location_id = db.Column(db.Integer)
	
	def __init__(self, name, email, phone_nr, location_id):
		self.name = name
		self.email = email
		self.phone_nr = phone_nr
		self.location_id = location_id
