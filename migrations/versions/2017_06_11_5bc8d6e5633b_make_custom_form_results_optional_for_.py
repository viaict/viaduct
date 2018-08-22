"""Make custom form results optional for transaction activity callbacks.

Revision ID: 5bc8d6e5633b
Revises: 8fc09a727a5c
Create Date: 2017-06-11 14:08:39.682872

"""
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5bc8d6e5633b'
down_revision = '8fc09a727a5c'


def upgrade():
    op.alter_column('transaction_activity', 'custom_form_result_id',
                    existing_type=mysql.INTEGER(display_width=11),
                    nullable=True)
    op.drop_constraint(
        'fk_transaction_activity_custom_form_result_id_custom_form_result',
        'transaction_activity', type_='foreignkey')
    op.create_foreign_key(op.f(
        'fk_transaction_activity_custom_form_result_id_custom_form_result'),
        'transaction_activity', 'custom_form_result',
        ['custom_form_result_id'], ['id'],
        ondelete='SET NULL')


def downgrade():
    op.drop_constraint(op.f(
        'fk_transaction_activity_custom_form_result_id_custom_form_result'),
        'transaction_activity', type_='foreignkey')
    op.create_foreign_key(
        'fk_transaction_activity_custom_form_result_id_custom_form_result',
        'transaction_activity', 'custom_form_result',
        ['custom_form_result_id'],
        ['id'])
    op.alter_column('transaction_activity', 'custom_form_result_id',
                    existing_type=mysql.INTEGER(display_width=11),
                    nullable=False)
