"""Add custom read permission table..

Revision ID: 21a2938dd9f5
Revises: 7525fd3b67d5
Create Date: 2018-02-10 16:20:52.218339

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '21a2938dd9f5'
down_revision = '7525fd3b67d5'


def upgrade():
    op.add_column('page_permission',
                  sa.Column('created', sa.DateTime(), nullable=True))
    op.add_column('page_permission',
                  sa.Column('modified', sa.DateTime(), nullable=True))

    op.add_column('page', sa.Column('custom_read_permission', sa.Boolean(),
                                    nullable=True))
    op.drop_column('page_permission', 'permission')
    op.rename_table('page_permission', 'page_read_permission')


def downgrade():
    op.rename_table('page_read_permission', 'page_permission')
    op.add_column('page_permission',
                  sa.Column('permission', mysql.INTEGER(display_width=11),
                            autoincrement=False, nullable=True))
    op.drop_column('page_permission', 'modified')
    op.drop_column('page_permission', 'created')
    op.drop_column('page', 'custom_read_permission')
    # ### end Alembic commands ###
