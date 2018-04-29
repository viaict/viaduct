"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

# op.get_bind() will fail when the migration is created,
# so catch the AttributeError
try:
    Base = declarative_base()
    db = sa
    Session = sessionmaker()

    conn = op.get_bind()
    session = Session(bind=conn)

    db.Model = Base
    db.relationship = relationship
    db.session = session
except AttributeError:
    pass


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}


# vim: ft=python
