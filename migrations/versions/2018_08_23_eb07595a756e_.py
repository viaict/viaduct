"""empty message.

Revision ID: eb07595a756e
Revises: ('18485381c9be', '42930577deff')
Create Date: 2018-08-23 11:34:14.693136

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = 'eb07595a756e'
down_revision = ('18485381c9be', '42930577deff')

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
