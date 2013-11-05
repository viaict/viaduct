from viaduct import db
import datetime

class CustomForm(db.Model):
	__tablename__ = 'custom_form'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	name			= db.Column(db.String(256))
	origin		= db.Column(db.String(4096))
	html			= db.Column(db.UnicodeText())
	max_attendants = db.Column(db.Integer)
	created		= db.Column(db.DateTime, default=datetime.datetime.now())
	owner = db.relationship('User', backref=db.backref('custom_forms', lazy='dynamic'))

	def __init__(self, owner_id=None, name="", origin="", html="", max_attendants=150):
		self.owner_id = owner_id
		self.name = name
		self.origin = origin
		self.html = html
		self.max_attendants = max_attendants

class CustomFormResult(db.Model):
	__tablename__ = 'custom_form_result'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	form_id		= db.Column(db.Integer)
	data			= db.Column(db.String(4096))
	is_reserve = db.Column(db.Boolean)
	has_payed	= db.Column(db.Boolean)
	created		= db.Column(db.DateTime, default=datetime.datetime.now())

	owner = db.relationship('User', backref=db.backref('custom_form_results', lazy='dynamic'))

	def __init__(self, owner_id=None, form_id=None, data="", is_reserve=False, has_payed=False):
		self.owner_id = owner_id
		self.form_id = form_id
		self.data = data
		self.is_reserve = is_reserve
		self.has_payed = has_payed

class CustomFormFollower(db.Model):
	__tablename__ = 'custom_form_follower'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	form_id		= db.Column(db.Integer)

	owner = db.relationship('User', backref=db.backref('custom_form_follower', lazy='dynamic'))

	def __init__(self, owner_id=None, form_id=None):
		self.owner_id = owner_id
		self.form_id = form_id

