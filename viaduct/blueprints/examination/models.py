import datetime

from viaduct import db

from viaduct.models import Course, Education
from viaduct.blueprints.user.models import User, UserPermission

class Examination(db.Model):
	__tablename__ = 'examination'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	path = db.Column(db.String(256), unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	timestamp = db.Column(db.DateTime)
	course_id = db.Column(db.Integer,
		db.ForeignKey('course.id'))
	education_id = db.Column(db.Integer,
		db.ForeignKey('education.id'))

	user = db.relationship(User,
		backref=db.backref('examinations', lazy='dynamic'))
	course = db.relationship(Course,
		backref=db.backref('examinations', lazy='dynamic'))
	education = db.relationship(Education,
		backref=db.backref('examinations', lazy='dynamic'))


	# course = db.relationship('Course', primaryjoin=(course_id==Course.id), backref=db.backref('examinations',
	# 	lazy='dynamic'))
	# education = db.relationship('Education', 
	# 	primaryjoin=(education_id==Education.id),
	# 	backref=db.backref('examinations',
	# 	lazy='dynamic'))


	def __init__(self, path, title, course, education, 
			timestamp=datetime.datetime.utcnow()):
		self.timestamp = timestamp
		self.path = path
		self.title = title
		self.course_id = course
		self.education_id = education
		
	# @staticmethod
	# def get_by_path(path):
	# 	return Page.query.filter(Page.path==path).first()

	# def has_revisions(self):
	# 	return self.revisions.count() > 0

	# def get_newest_revision(self):
	# 	return self.revisions.order_by(PageRevision.timestamp.desc()).first()


