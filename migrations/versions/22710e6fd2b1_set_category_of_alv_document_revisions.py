"""Set category of ALV document revisions.

Revision ID: 22710e6fd2b1
Revises: 4a3debf40b72
Create Date: 2018-03-14 15:35:30.841219

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from app.models.base_model import BaseEntity
from app.enums import FileCategory

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '22710e6fd2b1'
down_revision = '4a3debf40b72'

Base = declarative_base()
db = sa
db.Model = Base
db.relationship = relationship


class File(db.Model, BaseEntity):
    __tablename__ = 'file'

    hash = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20), nullable=False)

    category = db.Column(db.Enum(FileCategory), nullable=False)
    display_name = db.Column(db.String(200))


class Alv(db.Model, BaseEntity):
    __tablename__ = 'alv'

    minutes_file_id = db.Column(db.Integer, db.ForeignKey('file.id'),
                                nullable=True)
    minutes_file = db.relationship('File', foreign_keys=[minutes_file_id])


class AlvDocumentVersion(db.Model, BaseEntity):
    __tablename__ = 'alv_document_version'

    file_id = db.Column(db.Integer(), db.ForeignKey('file.id'))
    file = db.relationship('File')


def upgrade():
    connection = op.get_bind()
    Session = sa.orm.sessionmaker()
    session = Session(bind=connection)

    db.session = session

    minutes = db.session.query(File).join(Alv.minutes_file)
    documents = db.session.query(File).join(AlvDocumentVersion.file)
    files = documents.union(minutes).all()

    for f in files:
        f.category = FileCategory.ALV_DOCUMENT
        f.display_name = None

    db.session.commit()


def downgrade():
    pass
