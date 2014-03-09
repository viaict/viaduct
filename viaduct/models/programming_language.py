from viaduct import db
from viaduct.models import BaseEntity


class ProgrammingLanguage(db.Model, BaseEntity):
    __tablename__ = 'programming_language'

    title = db.Column(db.String(256))

    def __init__(self, title):
        self.title = title
