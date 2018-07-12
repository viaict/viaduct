"""empty message.

Revision ID: da44c279ce0a
Revises: ('fe6ff06f1f5b', '7d121969c6af', 'f1d5755ddc15')
Create Date: 2018-04-29 15:30:18.310232

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = 'da44c279ce0a'
down_revision = ('fe6ff06f1f5b', '7d121969c6af')

Base = declarative_base()
db = sa
db.Model = Base
db.relationship = relationship


def upgrade():
    pass


def downgrade():
    pass


# vim: ft=python
