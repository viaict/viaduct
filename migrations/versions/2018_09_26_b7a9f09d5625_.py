"""Add frontend DSN to database settings.

Revision ID: b7a9f09d5625
Revises: 68423db114cd
Create Date: 2018-09-26 15:48:56.853170

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = 'b7a9f09d5625'
down_revision = '68423db114cd'

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

    op.execute('''INSERT INTO setting (created, modified, key, value) VALUES(now(), now(), 'SENTRY_DSN_FRONTEND', 'https://d20fbd1634454649bd8877942ebb5657@sentry.io/1285048');''')


def downgrade():
    create_session()
    op.execute('''DELETE FROM setting WHERE key = 'SENTRY_DSN_FRONTEND';''')


# vim: ft=python
