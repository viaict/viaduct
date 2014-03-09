from viaduct import db
from viaduct.models import BaseEntity


class Requirement(db.Model, BaseEntity):
    __tablename__ = 'requirements'

    title = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(1024))

    def __init__(self, title, description):
        self.title = title
        self.description = description
