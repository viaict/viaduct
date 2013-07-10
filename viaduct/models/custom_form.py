from viaduct import db

class CustomForm(db.Model):
	__tablename__ = 'custom_form'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	name			= db.Column(db.String(256))
	origin		= db.Column(db.String(128))
	html			= db.Column(db.String(8192))
	
	owner = db.relationship('User', backref=db.backref('custom_forms', lazy='dynamic'))

	def __init__(self, owner_id=None, name="", origin="", html=""):
		self.owner_id = owner_id
		self.name = name
		self.origin = origin
		self.html = html

class CustomFormResult(db.Model):
	__tablename__ = 'custom_form_result'
	owner_id	= db.Column(db.Integer, primary_key=True)
	form_id		= db.Column(db.Integer, primary_key=True)
	data			= db.Column(db.String(2048))

	def __init__(self, owner_id=None, form_id=None, data=""):
		self.owner_id = owner_id
		self.form_id = form_id
		self.data= data
