from app import db
from app.models.base_model import BaseEntity


class Setting(db.Model, BaseEntity):
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.String(128))
