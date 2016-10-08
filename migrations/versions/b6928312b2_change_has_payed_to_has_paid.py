"""Change has_payed to has_paid

Revision ID: b6928312b2
Revises: 2105015bafe
Create Date: 2016-10-08 19:41:05.042167

"""

# revision identifiers, used by Alembic.
revision = 'b6928312b2'
down_revision = '2105015bafe'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.alter_column('custom_form_result', 'has_payed', new_column_name='has_paid', existing_type=sa.Boolean())
    op.alter_column('user', 'has_payed', new_column_name='has_paid', existing_type=sa.Boolean())
    op.alter_column('user', 'payed_date', new_column_name='paid_date', existing_type=sa.DateTime())
    op.alter_column('page', 'needs_payed', new_column_name='needs_paid', existing_type=sa.Boolean())

def downgrade():
    op.alter_column('custom_form_result', 'has_paid', new_column_name='has_payed', existing_type=sa.Boolean())
    op.alter_column('user', 'has_paid', new_column_name='has_payed', existing_type=sa.Boolean())
    op.alter_column('user', 'paid_date', new_column_name='payed_date', existing_type=sa.DateTime())
    op.alter_column('page', 'needs_paid', new_column_name='needs_payed', existing_type=sa.Boolean())
