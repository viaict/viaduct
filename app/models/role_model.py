from app import db
from app.models.base_model import BaseEntity


class GroupRole(db.Model, BaseEntity):
    """Many to Many between Groups and Roles."""

    prints = ("group", "role")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

    role = db.Column(db.String(128), nullable=False)

    def __str__(self):
        return self.role
