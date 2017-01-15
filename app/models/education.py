from app import db
from app.models import BaseEntity


class Education(db.Model, BaseEntity):
    __tablename__ = 'education'

    name = db.Column(db.String(128), nullable=False)

    def __init__(self, name):
        self.name = name
