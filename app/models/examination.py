from flask_babel import lazy_gettext as _

from app import db

from app.models.course import Course
from app.models.education import Education
from app.models.user import User
from app.models.file import File
from app.models.base_model import BaseEntity


test_types = {'Mid-term': _('Mid-Term'),
              'End-term': _('End-Term'),
              'Retake': _('Retake'),
              'Unknown': _('Unknown')}

test_type_default = 'Unknown'


class Examination(db.Model, BaseEntity):
    __tablename__ = 'examination'

    comment = db.Column(db.String(128))
    date = db.Column(db.Date)

    examination_file_id = db.Column(db.Integer, db.ForeignKey('file.id'),
                                    nullable=False)
    answers_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

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

    examination_file = db.relationship(
        File, foreign_keys=[examination_file_id], lazy='joined')
    answers_file = db.relationship(
        File, foreign_keys=[answers_file_id], lazy='joined')
