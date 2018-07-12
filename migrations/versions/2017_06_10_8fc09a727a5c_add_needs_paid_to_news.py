"""Add needs_paid to news.

Revision ID: 8fc09a727a5c
Revises: b42628364441
Create Date: 2017-06-10 12:43:55.512552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fc09a727a5c'
down_revision = 'b42628364441'


def upgrade():
    op.add_column('news', sa.Column('needs_paid', sa.Boolean(), nullable=False,
                                    default=False))


def downgrade():
    op.drop_column('news', 'needs_paid')
