"""Create group_role table.

Revision ID: 760cc9ca5d24
Revises: c633060ef804
Create Date: 2017-11-12 23:42:18.085381

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '760cc9ca5d24'
down_revision = 'c633060ef804'


def upgrade():
    op.create_table(
        'group_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'],
                                name=op.f(
                                    'fk_group_role_group_id_group')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_group_role')),
        sqlite_autoincrement=True
    )


def downgrade():
    op.drop_table('group_role')
