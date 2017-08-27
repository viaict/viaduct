from app import db
from app.models.base_model import BaseEntity


class File(db.Model, BaseEntity):
    """A file for pages and generic file usage."""

    __tablename__ = 'file'

    name = db.Column(db.String(200), unique=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    page = db.relationship('Page', backref=db.backref('files', lazy='dynamic'))

    def __init__(self, name='', page=None):
        """Constructor."""
        self.name = name
        self.page = page
