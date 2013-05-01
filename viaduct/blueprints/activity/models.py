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
	picture				= db.Column(db.String(255))
	venue					= db.Column(db.Integer) # venue ID
	updated_time	= db.Column(db.DateTime, default=datetime.datetime.utcnow())
	
	owner = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))

	# Automatically pick dates that make sense
	# Picture url to via_event logo
	# Default location to via kamer
	def __init__(self, owner_id, name, description, start_time, end_time, location, privacy, picture, venue):
		self.owner_id = owner_id
		self.name = name
		self.description = description
		self.start_time = start_time
		self.end_time = end_time
		self.location = location
		self.privacy = privacy
		self.picture = picture
		self.venue = 1

