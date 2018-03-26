"""Pimpy changes.

Revision ID: 7d121969c6af
Revises: 0563ce5ca262
Create Date: 2018-03-12 11:48:14.554607

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7d121969c6af'
down_revision = '0563ce5ca262'


def upgrade():
    connection = op.get_bind()
    connection.execute("""
        UPDATE pimpy_task SET minute_id = NULL, line = NULL WHERE minute_id = 1;
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
        UPDATE pimpy_task SET minute_id = 1, line = -1 WHERE minute_id IS NULL;
    """)
