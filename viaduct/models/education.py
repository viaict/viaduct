from viaduct import db
import datetime

class Education(db.Model):
	__tablename__ = 'education'

	id = db.Column(db.Integer, primary_key=True)
	degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'),
		nullable=False)
	name = db.Column(db.String(128), nullable=False)

	degree = db.relationship('Degree', backref=db.backref('educations',
		lazy='dynamic'))

	def __init__(self, degree_id, name):
		self.degree_id = degree_id
		self.name = name

