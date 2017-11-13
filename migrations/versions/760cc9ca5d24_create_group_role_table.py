"""Create group_role table.

Revision ID: 760cc9ca5d24
Revises: c633060ef804
Create Date: 2017-11-12 23:42:18.085381

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic.
from sqlalchemy.orm import Session

from app import Roles
from app.models.group import Group
from app.models.role_model import GroupRole

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
    op.drop_table('group_permission')

    bind = op.get_bind()
    session = Session(bind=bind)

    administrators = session.query(Group)\
        .filter_by(name='administrators').one_or_none()
    bc = session.query(Group)\
        .filter_by(name='BC').one_or_none()

    grouproles = []

    # Give administrators all roles.
    for role in Roles:
        gr = GroupRole()
        gr.group_id = administrators.id
        gr.role = role.value
        grouproles.append(gr)

    # Give committees pimpy and activity/form rights.
    for role in [Roles.ACTIVITY_WRITE, Roles.PIMPY_WRITE]:
        for group in [2, 20, 7, 31, 42, 25, 41, 44, 8, 9, 11, 12, 5, 46, 13,
                      37, 55, 14, 15, 45, 16, 30, 17, 10, 34, 47, 48]:
            gr = GroupRole()
            gr.group_id = group
            gr.role = role.value
            grouproles.append(gr)

    # Give BC additional rights.
    for role in [Roles.ACTIVITY_WRITE, Roles.PAGE_WRITE,
                 Roles.NAVIGATION_WRITE, Roles.FILE_WRITE]:
        gr = GroupRole()
        gr.group_id = bc.id
        gr.role = role.value

    # Custom rights.
    education_examination = GroupRole()
    education_examination.group_id = 16
    education_examination.role = Roles.EXAMINATION_WRITE.value
    grouproles.append(education_examination)

    domjudge_competitie = GroupRole()
    domjudge_competitie.group_id = 47
    domjudge_competitie.role = Roles.DOMJUDGE_ADMIN.value
    grouproles.append(domjudge_competitie)

    seo_marketing = GroupRole()
    seo_marketing.group_id = 15
    seo_marketing.role = Roles.SEO_WRITE.value
    grouproles.append(seo_marketing)

    presidium_alv = GroupRole()
    presidium_alv.group_id = 30
    presidium_alv.role = Roles.ALV_WRITE.value
    grouproles.append(presidium_alv)

    session.add_all(grouproles)
    session.commit()


def downgrade():
    op.drop_table('group_role')

    op.create_table(
        'group_permission',
        sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
        sa.Column('created', mysql.DATETIME(), nullable=True),
        sa.Column('modified', mysql.DATETIME(), nullable=True),
        sa.Column('module_name', mysql.TEXT(), nullable=True),
        sa.Column('group_id', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=True),
        sa.Column('permission', mysql.INTEGER(display_width=11),
                  autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'],
                                name='group_permission_ibfk_1'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default_charset='latin1',
        mysql_engine='InnoDB'
    )

    print("Fix your own rights.")
