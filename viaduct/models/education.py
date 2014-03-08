from viaduct import db
from viaduct.models import BaseEntity


class Education(db.Model, BaseEntity):
    __tablename__ = 'education'

    degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'),
                          nullable=False)
    name = db.Column(db.String(128), nullable=False)

    degree = db.relationship('Degree', backref=db.backref('educations',
                             lazy='dynamic'))

    def __init__(self, degree_id, name):
        self.degree_id = degree_id
        self.name = name
