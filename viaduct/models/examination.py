import datetime
import os

from viaduct import application, db

from viaduct.models.page import IdRevision
from viaduct.models.course import Course
from viaduct.models.education import Education
from viaduct.models.user import User
from viaduct.models import BaseEntity

FILE_FOLDER = application.config['EXAMINATION_FILE_FOLDER']


class ExaminationRevision(IdRevision):
    __tablename__ = 'examination_revision'

    path = db.Column(db.String(256))
    answer_path = db.Column(db.String(256))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('examination_revisions',
                                                      lazy='dynamic'))

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course',
                             backref=db.backref('examination_revisions',
                                                lazy='dynamic'))

    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    education = db.relationship('Education',
                                backref=db.backref('examination_revisions',
                                                   lazy='dynamic'))

    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    page = db.relationship('Page', backref=db.backref('examination_revisions',
                                                      lazy='dynamic'))

    def __init__(self, page=None, title='', comment='', instance_id=None,
                 path='', answer_path='', author_id=None, course_id=None,
                 education_id=None):
        super(ExaminationRevision, self).__init__(title, comment, instance_id)

        self.page = page

        self.path = path
        self.answer_path = answer_path
        self.author_id = author_id
        self.course_id = course_id
        self.education_id = education_id

    def get_path(self):
        return os.path.join(FILE_FOLDER, self.path)

    def get_answer_path(self):
        return os.path.join(FILE_FOLDER, self.answer_path)
