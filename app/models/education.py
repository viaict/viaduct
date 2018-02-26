from app import db
from app.models.base_model import BaseEntity


class Education(db.Model, BaseEntity):
    __tablename__ = 'education'

    name = db.Column(db.String(128), nullable=False)
