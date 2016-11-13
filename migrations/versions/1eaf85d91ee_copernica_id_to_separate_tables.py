from alembic import op
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

"""copernica_id to separate tables

Revision ID: 1eaf85d91ee
Revises: 48c16211f99
Create Date: 2016-11-12 13:55:00.093625

"""

# revision identifiers, used by Alembic.
revision = '1eaf85d91ee'
down_revision = '48c16211f99'

NEWSLETTER_DB_ID = 10
RECEIVE_INFORMATION_DB_ID = 24

Base = declarative_base()
Session = sessionmaker()


class MailingList(Base):
    __tablename__ = "mailing_list"

    id = sa.Column(sa.Integer(), primary_key=True)
    created = sa.Column(sa.DateTime(), default=datetime.now)
    modified = sa.Column(sa.DateTime(), default=datetime.now,
                         onupdate=datetime.now)
    name = sa.Column(sa.String(64))  # display name
    copernica_db_id = sa.Column(sa.Integer())
    active = sa.column(sa.Boolean())
    member_only = sa.column(sa.Boolean())

    def __init__(self, name="", db_id=0,
                 active=False, member_only=True):
        self.name = name
        self.copernica_db_id = db_id
        self.active = active
        self.member_only = member_only


class MailingListUser(Base):
    __tablename__ = "mailing_list_user"

    id = sa.Column(sa.Integer(), primary_key=True)
    created = sa.Column(sa.DateTime(), default=datetime.now)
    modified = sa.Column(sa.DateTime(),
                         default=datetime.now,
                         onupdate=datetime.now)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey('user.id'))
    user = relationship('User',
                        backref=backref('mailinglists',
                                        lazy='dynamic'))
    mailing_list_id = sa.Column(sa.Integer(),
                                sa.ForeignKey('mailing_list.copernica_db_id'))
    mailing_list = relationship('MailingList',
                                backref=backref('followers',
                                                lazy='dynamic'))
    copernica_user_id = sa.Column(sa.Integer())
    subscribed = sa.Column(sa.Boolean(), default=False)


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer(), primary_key=True)
    created = sa.Column(sa.DateTime(), default=datetime.now)
    modified = sa.Column(sa.DateTime(), default=datetime.now,
                         onupdate=datetime.now)
    copernica_id = sa.Column(sa.Integer(), nullable=True)
    receive_information = sa.Column(sa.Boolean(), default=False)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.create_table('mailing_list',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.String(length=64), nullable=True),
                    sa.Column('copernica_db_id', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id',
                                            name=op.f('pk_mailing_list')),
                    sqlite_autoincrement=True)
    op.create_table('mailing_list_user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('mailing_list_id', sa.Integer(), nullable=True),
                    sa.Column('copernica_user_id',
                              sa.Integer(),
                              nullable=True),
                    sa.Column('subscribed', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id',
                                            name=op.f('pk_mailing_list_user')),
                    sqlite_autoincrement=True)
    # Data migration
    newsletter = MailingList('newsletter', NEWSLETTER_DB_ID, True, True)
    session.add(newsletter)
    via_company_information = MailingList('company information',
                                          RECEIVE_INFORMATION_DB_ID,
                                          True,
                                          True)
    session.add(via_company_information)
    for user in session.query(User):
        mailing_list_user = MailingListUser()
        mailing_list_user.user_id = user.id
        mailing_list_user.mailing_list_id = NEWSLETTER_DB_ID
        mailing_list_user.copernica_user_id = user.copernica_id
        mailing_list_user.subscribed = False
        session.add(mailing_list_user)
        if user.receive_information:
            receive_information = MailingListUser()
            receive_information.user_id = user.id
            receive_information.mailing_list_id = RECEIVE_INFORMATION_DB_ID
            receive_information.copernica_user_id = 0
            receive_information.subscribed = True
            session.add(receive_information)
    session.commit()
    op.drop_column('user', 'copernica_id')
    op.drop_column('user', 'receive_information')


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.add_column('user',
                  sa.Column('receive_information',
                            mysql.TINYINT(display_width=1),
                            autoincrement=False,
                            nullable=True))
    op.add_column('user',
                  sa.Column('copernica_id',
                            mysql.INTEGER(display_width=11),
                            autoincrement=False,
                            nullable=True))
    # Data migration for standard Copernica_id and receive_information
    # all other mailinglists are lost...
    for mailing_list_user in session.query(MailingListUser):
        if mailing_list_user.mailing_list_id == NEWSLETTER_DB_ID:
            user = session.query(User).filter_by(id=mailing_list_user.user_id)\
                .first()
            user.copernica_id = mailing_list_user.copernica_user_id
            session.add(user)
        elif mailing_list_user.mailing_list_id == RECEIVE_INFORMATION_DB_ID:
            user = session.query(User).filter_by(id=mailing_list_user.user_id)\
                .first()
            user.receive_information = True
            session.add(user)
    for user in session.query(User):
        if user.receive_information is None:
            user.receive_information = False
            session.add(user)
    session.commit()
    op.drop_table('mailing_list_user')
    op.drop_table('mailing_list')
