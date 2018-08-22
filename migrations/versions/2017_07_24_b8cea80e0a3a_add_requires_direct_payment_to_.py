"""Add requires_direct_payment to CustomForm.

Revision ID: b8cea80e0a3a
Revises: 5bc8d6e5633b
Create Date: 2017-07-24 14:26:57.045590

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b8cea80e0a3a'
down_revision = '5bc8d6e5633b'


def upgrade():
    op.add_column('custom_form',
                  sa.Column('requires_direct_payment', sa.Boolean(),
                            nullable=False))


def downgrade():
    op.drop_column('custom_form', 'requires_direct_payment')
