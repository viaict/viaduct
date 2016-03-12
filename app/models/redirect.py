from app import db
from app.models import BaseEntity


class Redirect(db.Model, BaseEntity):
    __tablename__ = 'redirect'

    fro = db.Column(db.String(200), unique=True)
    to = db.Column(db.String(200))

    def __init__(self, fro, to):
        self.fro = fro
        self.to = to
