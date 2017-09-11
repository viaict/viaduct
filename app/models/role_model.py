from app import db
from app.models.base_model import BaseEntity


class GroupRole(db.Model, BaseEntity):
    """Relationship from group to roles."""

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

    role = db.Column(db.String(128), nullable=False)
