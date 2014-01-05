#!/usr/bin/python

from viaduct import db, login_manager
from viaduct.models.education import Education


class User(db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), unique=True)
	password = db.Column(db.String(60))
	first_name = db.Column(db.String(256))
	last_name = db.Column(db.String(256))
	has_payed = db.Column(db.Boolean)
	shirt_size = db.Column(db.Enum('Small', 'Medium', 'Large'))
	allergy = db.Column(db.String(1024))  # Allergy / medication
	diet = db.Column(db.Enum('Vegetarisch', 'Veganistisch', 'Fruitarier'))
	gender = db.Column(db.Enum('Man', 'Vrouw', 'Geen info'))
	phone_nr = db.Column(db.String(16))
	emergency_phone_nr = db.Column(db.String(16))
	description = db.Column(db.String(1024))  # Description of user
	student_id = db.Column(db.String(256))
	education_id = db.Column(db.Integer, db.ForeignKey('education.id'))

	education = db.relationship(Education,
								backref=db.backref('user', lazy='dynamic'))

	def __init__(self, email=None, password=None, first_name=None,
				last_name=None, student_id=None, education_id=None):
		if not email:
			self.id = 0

		self.email = email
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
		self.student_id = student_id
		self.education_id = education_id

	def is_authenticated(self):
		"""Necessary."""
		return self.id != 0

	def is_active(self):
		"""Necessary."""
		return self.id != 0

	def is_anonymous(self):
		return self.id == 0

	def get_id(self):
		"""Necessary for Flask-Login."""
		return unicode(self.id)

	@property
	def name(self):
		"""The user's name."""
		return ' '.join([self.first_name, self.last_name])

	@staticmethod
	def get_anonymous_user():
		return User.query.get(0)

	def __repr__(self):
		return '<User({0}, "{1}", "{2}", "{3}", "{4}", "{5}">'\
			.format(self.id, self.email, self.password, self.first_name,
					self.last_name, self.student_id)
