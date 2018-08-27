"""empty message.

Revision ID: 7ca72c9f0188
Revises: ('42930577deff', '18485381c9be')
Create Date: 2018-08-22 17:37:58.985763

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '7ca72c9f0188'
down_revision = ('42930577deff', '18485381c9be')

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
