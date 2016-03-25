import datetime

from flask.ext.babel import lazy_gettext as _

from app import db

from app.models.course import Course
from app.models.education import Education
from app.models.user import User
from app.models import BaseEntity


test_types = {'Mid-term': _('Mid-Term'),
              'End-term': _('End-Term'),
              'Retake': _('Retake'),
              'Unknown': _('Unknown')}

test_type_default = 'Unknown'


class Examination(db.Model, BaseEntity):
    __tablename__ = 'examination'

    title = db.Column(db.String(128))
    path = db.Column(db.String(256))
    answer_path = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)
    course_id = db.Column(db.Integer,
                          db.ForeignKey('course.id'))
    education_id = db.Column(db.Integer,
                             db.ForeignKey('education.id'))
    test_type = db.Column(db.Enum(*test_types.keys()),
                          nullable=False, server_default='Unknown')
    user = db.relationship(User,
                           backref=db.backref('examinations', lazy='dynamic'))
    course = db.relationship(Course,
                             backref=db.backref('examinations', lazy='dynamic')
                             )
    education = db.relationship(Education,
                                backref=db.backref('examinations',
                                                   lazy='dynamic'))

    def __init__(self, path, title, course_id, education_id,
                 timestamp=datetime.datetime.utcnow(), answers='',
                 test_type=test_type_default):
        self.timestamp = timestamp
        self.path = path
        self.title = title
        self.course_id = course_id
        self.education_id = education_id
        self.answer_path = answers
        self.test_type = test_type
