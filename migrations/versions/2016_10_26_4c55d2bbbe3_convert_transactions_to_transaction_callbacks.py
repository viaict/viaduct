from alembic import op
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.dialects import mysql
import sqlalchemy as sa
"""Convert transactions to transaction callbacks

Revision ID: 4c55d2bbbe3
Revises: 48c16211f99
Create Date: 2016-10-26 11:16:59.622130

"""

# revision identifiers, used by Alembic.
revision = '4c55d2bbbe3'
down_revision = '48c16211f99'


Base = declarative_base()
Session = sessionmaker()


class Transaction(Base):
    __tablename__ = 'mollie_transaction'

    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, default=datetime.now)
    modified = sa.Column(sa.DateTime, default=datetime.now,
                         onupdate=datetime.now)
    mollie_id = sa.Column(sa.String(256))
    status = sa.Column(
        sa.Enum('open', 'cancelled', 'paidout', 'paid', 'expired'))

    form_result_id = sa.Column(sa.Integer,
                               sa.ForeignKey('custom_form_result.id'))

    def __init__(self, status='open'):
        self.status = status


class TransactionActivity(Base):

    __tablename__ = 'transaction_activity'

    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, default=datetime.now)
    modified = sa.Column(sa.DateTime, default=datetime.now,
                         onupdate=datetime.now)
    custom_form_result_id = sa.Column(sa.Integer(),
                                      sa.ForeignKey('custom_form_result.id'),
                                      nullable=False)
    transaction_id = sa.Column(sa.Integer(),
                               sa.ForeignKey('mollie_transaction.id'))

    transaction = relationship('Transaction')


class CustomFormResult(Base):
    __tablename__ = 'custom_form_result'

    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, default=datetime.now)
    modified = sa.Column(sa.DateTime, default=datetime.now,
                         onupdate=datetime.now)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.create_table(
        'transaction_activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('custom_form_result_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['transaction_id'],
            ['mollie_transaction.id'],
            name=op.f(
                'fk_transaction_activity_transaction_id_mollie_transaction')),
        sa.ForeignKeyConstraint(
            ['custom_form_result_id'],
            ['custom_form_result.id'],
            name=op.f(
                'fk_transaction_activity_custom_form_result_id_custom_form_result')),  # noqa
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transaction_activity')),
        sqlite_autoincrement=True
    )

    for transaction in session.query(Transaction):
        if transaction.form_result_id:
            product = TransactionActivity()
            product.transaction_id = transaction.id
            product.custom_form_result_id = transaction.form_result_id
            session.add(product)
    session.commit()

    op.drop_constraint('mollie_transaction_ibfk_1',
                       'mollie_transaction',
                       type_='foreignkey')
    op.drop_column('mollie_transaction', 'form_result_id')

    op.create_table(
        'transaction_membership',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['transaction_id'],
            ['mollie_transaction.id'],
            name=op.f(
                'fk_transaction_membership_transaction_id_mollie_transaction')
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
            name=op.f('fk_transaction_membership_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transaction_membership')),
        sqlite_autoincrement=True
    )

    op.alter_column('mollie_transaction', 'status',
                    nullable=False,
                    type_=sa.Enum('open', 'cancelled', 'pending', 'expired',
                                  'failed', 'paid', 'paidout', 'refunded',
                                  'charged_back'),
                    existing_type=sa.Enum('open', 'cancelled',
                                          'paidout', 'paid', 'expired'),
                    existing_nullable=True)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column('mollie_transaction',
                  sa.Column(
                      'form_result_id',
                      mysql.INTEGER(display_width=11),
                      autoincrement=False,
                      nullable=True))
    op.create_foreign_key('mollie_transaction_ibfk_1',
                          'mollie_transaction',
                          'custom_form_result',
                          ['form_result_id'], ['id'])

    for transaction_act in session.query(TransactionActivity):
        if transaction_act.transaction_id:
            transaction = session.query(Transaction)\
                .get(transaction_act.transaction_id)
            transaction.form_result_id = transaction_act.custom_form_result_id
    session.commit()

    op.drop_table('transaction_membership')
    op.drop_table('transaction_activity')
