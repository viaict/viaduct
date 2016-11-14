from alembic import op

"""copernica relations

Revision ID: 4e7ae4a896e
Revises: 1eaf85d91ee
Create Date: 2016-11-14 14:07:37.349845

"""

# revision identifiers, used by Alembic.
revision = '4e7ae4a896e'
down_revision = '1eaf85d91ee'


def upgrade():
    op.create_unique_constraint(
        op.f('uq_mailing_list_copernica_db_id'),
        'mailing_list',
        ['copernica_db_id'])
    op.drop_index(
        'fk_mailing_list_user_user_id_user',
        table_name='mailing_list_user')
    op.create_foreign_key(
        op.f('fk_mailing_list_user_mailing_list_id_mailing_list'),
        'mailing_list_user',
        'mailing_list',
        ['mailing_list_id'],
        ['copernica_db_id'])
    op.create_foreign_key(
        op.f('fk_mailing_list_user_user_id_user'),
        'mailing_list_user',
        'user',
        ['user_id'],
        ['id'])


def downgrade():
    op.drop_constraint(
        op.f('fk_mailing_list_user_user_id_user'),
        'mailing_list_user',
        type_='foreignkey')
    op.drop_constraint(
        op.f('fk_mailing_list_user_mailing_list_id_mailing_list'),
        'mailing_list_user',
        type_='foreignkey')
    op.create_index(
        'fk_mailing_list_user_user_id_user',
        'mailing_list_user',
        ['user_id'],
        unique=False)
    op.drop_constraint(
        op.f('uq_mailing_list_copernica_db_id'),
        'mailing_list',
        type_='unique')
