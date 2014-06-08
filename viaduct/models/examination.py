import datetime

from viaduct import db

from viaduct.models.page import IdRevision
from viaduct.models.course import Course
from viaduct.models.education import Education
from viaduct.models.user import User
from viaduct.models import BaseEntity


class ExaminationRevision(IdRevision):
    __tablename__ = 'examination_revision'

    path = db.Column(db.String(256))
    answer_path = db.Column(db.String(256))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('examination_revisions',
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
                 path='', answer_path='', user_id=None, course_id=None,
                 education_id=None):
        super(ExaminationRevision, self).__init__(title, comment, instance_id)

        self.page = page

        self.path = path
        self.answer_path = answer_path
        self.user_id = user_id
        self.course_id = course_id
        self.education_id = education_id
