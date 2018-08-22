"""Cascade minute deletion

Revision ID: bef47d0853
Revises: 3769b81bfaf
Create Date: 2015-10-10 14:23:04.126879

"""

# revision identifiers, used by Alembic.
revision = 'bef47d0853'
down_revision = '3769b81bfaf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_constraint('pimpy_task_ibfk_1', 'pimpy_task', type_='foreignkey')
    op.create_foreign_key('pimpy_task_minute_fk', 'pimpy_task', 'pimpy_minute',
                          ['minute_id'], ['id'], ondelete='cascade')

    op.drop_constraint('pimpy_task_user_ibfk_1', 'pimpy_task_user',
                       type_='foreignkey')
    op.create_foreign_key('pimpy_task_user_task_fk', 'pimpy_task_user',
                          'pimpy_task', ['task_id'], ['id'],
                          ondelete='cascade')

def downgrade():
    op.drop_constraint('pimpy_task_minute_fk', 'pimpy_task',
                       type_='foreignkey')
    op.create_foreign_key('pimpy_task_ibfk_1', 'pimpy_task', 'pimpy_minute',
                          ['minute_id'], ['id'])

    op.drop_constraint('pimpy_task_user_task_fk', 'pimpy_task_user',
                       type_='foreignkey')
    op.create_foreign_key('pimpy_task_user_ibfk_1', 'pimpy_task_user',
                          'pimpy_task', ['task_id'], ['id'])
