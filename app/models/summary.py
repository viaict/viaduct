from app import db

from app.models.course import Course
from app.models.education import Education
from app.models.base_model import BaseEntity


class Summary(db.Model, BaseEntity):
    __tablename__ = 'summary'

    title = db.Column(db.String(128))
    path = db.Column(db.String(256))
    date = db.Column(db.Date)
    course_id = db.Column(db.Integer,
                          db.ForeignKey('course.id'))
    education_id = db.Column(db.Integer,
                             db.ForeignKey('education.id'))

    course = db.relationship(Course,
                             backref=db.backref('summary', lazy='dynamic'))
    education = db.relationship(Education,
                                backref=db.backref('summary',
                                                   lazy='dynamic'))

    def __init__(self, title, path, date, course_id, education_id):
        self.title = title
        self.path = path
        self.date = date
        self.course_id = course_id
        self.education_id = education_id
