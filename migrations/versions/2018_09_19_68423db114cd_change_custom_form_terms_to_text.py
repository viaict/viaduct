"""Change custom form terms to text.

Revision ID: 68423db114cd
Revises: 7135c4a2339e
Create Date: 2018-09-19 21:29:08.800064

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = '68423db114cd'
down_revision = '7135c4a2339e'

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
    op.alter_column('custom_form', 'terms', type_=sa.Text,
                    existing_type=sa.String)

    pass


def downgrade():
    create_session()

    op.alter_column('custom_form', 'terms', type_=sa.String,
                    existing_type=sa.Text)

    pass

# vim: ft=python
