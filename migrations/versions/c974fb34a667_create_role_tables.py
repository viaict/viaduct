"""Create role tables.

Revision ID: c974fb34a667
Revises: e28438a52376
Create Date: 2017-08-15 16:59:33.228928

"""
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

# from app.models.role_model import Role
from app.roles import Roles

revision = 'c974fb34a667'
down_revision = 'e28438a52376'


def upgrade():
    op.create_table(
        'group_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'],
                                name=op.f(
                                    'fk_group_role_group_id_group')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_group_role')),
        sqlite_autoincrement=True
    )


def downgrade():
    op.drop_table('group_role')
