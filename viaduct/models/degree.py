from viaduct import db
from viaduct.models import BaseEntity


class Degree(db.Model, BaseEntity):
    __tablename__ = 'degree'

    name = db.Column(db.String(128), nullable=False)
    abbreviation = db.Column(db.String(128), nullable=False)

    def __init__(self, name, abbreviation):
        self.name = name
        self.abbreviation = abbreviation
