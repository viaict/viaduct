from app import db
from app.models.base_model import BaseEntity


class PasswordTicket(db.Model, BaseEntity):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
