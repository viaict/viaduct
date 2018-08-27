"""empty message.

Revision ID: c008583e8f8d
Revises: ('0d279cc03c6e', '384cb6885818')
Create Date: 2018-05-26 17:57:08.890229

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = 'c008583e8f8d'
down_revision = ('0d279cc03c6e', '384cb6885818')

Base = declarative_base()
db = sa
db.Model = Base
db.relationship = relationship


def create_session():
    connection = op.get_bind()
    session_maker = sa.orm.sessionmaker()
    session = session_maker(bind=connection)
    db.session = session


def upgrade():
    create_session()

    pass


def downgrade():
    create_session()

    pass


# vim: ft=python
