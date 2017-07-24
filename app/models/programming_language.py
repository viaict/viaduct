from app import db
from app.models.base_model import BaseEntity


class ProgrammingLanguage(db.Model, BaseEntity):
    __tablename__ = 'programming_language'

    title = db.Column(db.String(256))

    def __init__(self, title):
        self.title = title
