from viaduct import db

class CustomForm(db.Model):
	__tablename__ = 'custom_form'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	name			= db.Column(db.String(256))
	origin		= db.Column(db.String(4096))
	html			= db.Column(db.UnicodeText())

	owner = db.relationship('User', backref=db.backref('custom_forms', lazy='dynamic'))

	def __init__(self, owner_id=None, name="", origin="", html=""):
		self.owner_id = owner_id
		self.name = name
		self.origin = origin
		self.html = html

class CustomFormResult(db.Model):
	__tablename__ = 'custom_form_result'

	id				= db.Column(db.Integer, primary_key=True)
	owner_id	= db.Column(db.Integer, db.ForeignKey('user.id'))
	form_id		= db.Column(db.Integer)
	data			= db.Column(db.String(4096))
	has_payed	= db.Column(db.Boolean)

	owner = db.relationship('User', backref=db.backref('custom_form_results', lazy='dynamic'))

	def __init__(self, owner_id=None, form_id=None, data="", has_payed=False):
		self.owner_id = owner_id
		self.form_id = form_id
		self.data= data
		self.has_payed = has_payed
