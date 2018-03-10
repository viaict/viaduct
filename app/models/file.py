from app import db
from app.models.base_model import BaseEntity
from app.enums import FileCategory


class File(db.Model, BaseEntity):
    """Contains the metadata of an uploaded file."""

    __tablename__ = 'file'

    hash = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20), nullable=False)

    category = db.Column(db.Enum(FileCategory), nullable=False)
    display_name = db.Column(db.String(200), unique=True)
