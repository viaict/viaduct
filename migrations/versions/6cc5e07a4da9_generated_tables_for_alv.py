"""Generated tables for ALV.

Revision ID: 6cc5e07a4da9
Revises: b8cea80e0a3a
Create Date: 2017-07-31 00:09:05.562370

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6cc5e07a4da9'
down_revision = 'b8cea80e0a3a'


def upgrade():
    op.create_table(
        'alv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('nl_name', sa.String(length=128), nullable=True),
        sa.Column('en_name', sa.String(length=128), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.Column('chairman_user_id', sa.Integer(), nullable=True),
        sa.Column('secretary_user_id', sa.Integer(),
                  nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activity.id'],
                                name=op.f(
                                    'fk_alv_activity_id_activity')),
        sa.ForeignKeyConstraint(['chairman_user_id'], ['user.id'],
                                name=op.f(
                                    'fk_alv_chairman_user_id_user')),
        sa.ForeignKeyConstraint(['secretary_user_id'], ['user.id'],
                                name=op.f(
                                    'fk_alv_secretary_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_alv')),
        sqlite_autoincrement=True
    )
    op.create_table(
        'alv_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('nl_name', sa.String(length=128),
                  nullable=False),
        sa.Column('en_name', sa.String(length=128),
                  nullable=False),
        sa.Column('alv_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['alv_id'], ['alv.id'], name=op.f(
            'fk_alv_document_alv_id_alv')),
        sa.PrimaryKeyConstraint('id',
                                name=op.f('pk_alv_document')),
        sqlite_autoincrement=True
    )
    op.create_table(
        'alv_document_version',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('alv_document_id', sa.Integer(), nullable=True),
        sa.Column('final', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['alv_document_id'],
                                ['alv_document.id'], name=op.f(
                'fk_alv_document_version_alv_document_id_alv_document')),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'],
                                name=op.f(
                                    'fk_alv_document_version_file_id_file')),
        sa.PrimaryKeyConstraint('id', name=op.f(
            'pk_alv_document_version')),
        sqlite_autoincrement=True
    )


def downgrade():
    op.drop_table('alv_document_version')
    op.drop_table('alv_document')
    op.drop_table('alv')
