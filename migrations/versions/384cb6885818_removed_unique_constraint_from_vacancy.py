"""Removed unique constraint from vacancy.

Revision ID: 384cb6885818
Revises: da44c279ce0a
Create Date: 2018-05-08 10:47:33.652182

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '384cb6885818'
down_revision = 'da44c279ce0a'

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

    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('uq_vacancy_title', table_name='vacancy')
    # ### end Alembic commands ###


def downgrade():
    create_session()

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('uq_vacancy_title', 'vacancy', ['title'], unique=True)
    # ### end Alembic commands ###


# vim: ft=python
