"""empty message.

Revision ID: 596d0ca91b33
Revises: ('eb07595a756e', '7ca72c9f0188')
Create Date: 2018-08-23 12:19:35.928161

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '596d0ca91b33'
down_revision = ('eb07595a756e', '7ca72c9f0188')

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
