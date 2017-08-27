from app import db
from app.models.base_model import BaseEntity


class GroupRole(db.Model, BaseEntity):
    """Many to Many between Groups and Roles."""

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role')


class Role(db.Model, BaseEntity):
    """Role used to secure the application."""
    role = db.Column(db.String(128), nullable=False)
