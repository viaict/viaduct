from viaduct import db
from viaduct.models import BaseEntity

education_course = db.Table(
    'education_course',
    db.Column('education_id', db.Integer, db.ForeignKey('education.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)


class Course(db.Model, BaseEntity):
    __tablename__ = 'course'

    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=False)

    educations = db.relationship('Education', secondary=education_course,
                                 backref=db.backref('courses', lazy='dynamic'),
                                 lazy='dynamic')

    def __init__(self, name, description):
        self.name = name
        self.description = description
