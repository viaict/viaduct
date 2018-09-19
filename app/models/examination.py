from flask_babel import lazy_gettext as _
import re

from app import db

from app.models.course import Course
from app.models.education import Education
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

    timestamp = db.Column(db.DateTime)
    course_id = db.Column(db.Integer,
                          db.ForeignKey('course.id'))
    education_id = db.Column(db.Integer,
                             db.ForeignKey('education.id'))
    test_type = db.Column(db.Enum(*list(test_types.keys()),
                                  name='examination_type'),
                          nullable=False, server_default='Unknown')
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

    def _get_filename(self, answers):
        fn = ""

        for word in re.split(r"\s+", self.course.name):
            fn += word[0].upper() + word[1:].lower()

        if self.test_type == 'Mid-term':
            fn += "_Midterm"
        elif self.test_type == 'End-term':
            fn += "_Final"
        elif self.test_type == 'Retake':
            fn += "_Retake"

        if self.date is not None:
            fn += self.date.strftime("_%d_%m_%Y")

        if answers:
            fn += "_answers"

        return fn

    @property
    def examination_filename(self):
        """
        Filename for the examination file (without extension).

        Create a filename for the examination file
        based on the exam's information.
        """
        return self._get_filename(False)

    @property
    def answers_filename(self):
        """
        Filename for the answers file file (without extension).

        Create a filename for the answers file
        based on the exam's information.
        """

        if self.answers_file is None:
            return None
        return self._get_filename(True)
