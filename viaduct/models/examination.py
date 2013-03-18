import datetime

from viaduct import db

class Examination(db.Model):
	__tablename__ = 'examination'

	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

	course = db.relationship('Course', backref=db.backref('examinations',
		lazy='dynamic'))

