from viaduct import db


class Degree(db.Model):
    __tablename__ = 'degree'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    abbreviation = db.Column(db.String(128), nullable=False)

    def __init__(self, name, abbreviation):
        self.name = name
        self.abbreviation = abbreviation
