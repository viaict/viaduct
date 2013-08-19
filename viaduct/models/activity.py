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
	form_id				= db.Column(db.Integer, db.ForeignKey('custom_form.id'))

	owner = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))

	def __init__(self, owner_id=None, name="", description="", start_time=None, end_time=None, location="Sciencepark, Amsterdam", privacy="public", price="gratis", picture=None, venue=1, form_id=None):
		if not start_time:
			today = datetime.datetime.now()
			start_time = datetime.datetime(today.year, today.month, today.day, 17)
			end_time	 = start_time + datetime.timedelta(hours=5)

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
		self.form_id = form_id

	def __repr__(self):
		return '<Activity(%s, "%s", "%s")>' % (self.id, self.start_time,
					self.end_time)

	def get_time(self):
		if self.start_time.month == self.end_time.month:
			if self.start_time.day == self.end_time.day:
				return self.start_time.strftime("%A %d %b, %H:%M - ") + self.end_time.strftime("%H:%M")
			else:
				return self.start_time.strftime("%a. %d %b (%H:%M) - ") + \
					self.end_time.strftime("%a. %d (%H:%M) %b")

	def get_short_description(self, characters):

		if (len(self.description) > characters):
			short_description = self.description[:characters].strip()
			words = short_description.split(' ')[:-1]

			return ' '.join(words) + '...'

		return self.description
