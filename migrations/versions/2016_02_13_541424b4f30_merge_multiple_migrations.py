"""Merge multiple migrations

Revision ID: 541424b4f30
Revises: ('49f0e0933ec', '5088a7fdf2')
Create Date: 2016-02-13 18:37:09.994014

"""

# revision identifiers, used by Alembic.
revision = '541424b4f30'
down_revision = ('49f0e0933ec', '5088a7fdf2')

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
