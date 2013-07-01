from viaduct import db
import datetime

# Model to support Facebook/Google API integration
class Activity(db.Model):
	__tablename__ = 'activity'

	id						= db.Column(db.Integer, primary_key=True)
	owner_id			= db.Column(db.Integer, db.ForeignKey('user.id'))
	name					= db.Column(db.String(256))
	description		= db.Column(db.String(2048))
	start_time		= db.Column(db.DateTime)
	end_time			= db.Column(db.DateTime)
	location			= db.Column(db.String(64))
	privacy				= db.Column(db.String(64))
	price					= db.Column(db.String(16))
	picture				= db.Column(db.String(255))
	venue					= db.Column(db.Integer) # venue ID
	updated_time	= db.Column(db.DateTime, default=datetime.datetime.now())
	
	owner = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))

	def __init__(self, owner_id=None, name="", description="", start_time=datetime.datetime.now(), end_time=datetime.datetime.now(), location="Sciencepark, Amsterdam", privacy="public", price="gratis", picture=None, venue=1):
		self.owner_id = owner_id
		self.name = name
		self.description = description
		self.start_time = start_time
		self.end_time = end_time
		self.location = location
		self.privacy = privacy
		self.price = price
		self.picture = picture
		self.venue = 1

	def __repr__(self):
		return '<Activity(%s, "%s", "%s")>' % (self.id, self.start_time,
					self.end_time)

	def get_time(self):
		if self.start_time.month == self.end_time.month:
			if self.start_time.day == self.end_time.day:
				return self.start_time.strftime("%A %d %b, %H:%M - ") + self.end_time.strftime("%H:%M") 
			else:
				return self.start_time.strftime("%a. %d %b (%H:%M) - ")  + \
					self.end_time.strftime("%a. %d (%H:%M) %b") 

