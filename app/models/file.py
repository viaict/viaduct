from app import db
from app.models.base_model import BaseEntity
from app.enums import FileCategory
from sqlalchemy import UniqueConstraint


class File(db.Model, BaseEntity):
    """Contains the metadata of an uploaded file."""

    __tablename__ = 'file'

    hash = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20), nullable=False)

    category = db.Column(db.Enum(FileCategory, name='file_category'),
                         nullable=False)
    display_name = db.Column(db.String(200))

    @property
    def full_display_name(self):
        if not self.display_name:
            return None

        name = self.display_name
        if len(self.extension) > 0:
            name += "." + self.extension

        return name

    __table_args__ = (UniqueConstraint('display_name', 'extension'),)
