from app import db
import datetime
from app.models import BaseEntity


class Password_ticket(db.Model, BaseEntity):
    __tablename__ = 'password_ticket'

    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    hash = db.Column(db.String(64), nullable=False)

    def __init__(self, user_id=None, hash=None):
        self.created_on = datetime.datetime.now()
        self.user = user_id
        self.hash = hash
