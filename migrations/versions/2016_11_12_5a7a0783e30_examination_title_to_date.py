"""Examination title to date

Revision ID: 5a7a0783e30
Revises: 48c16211f99
Create Date: 2016-11-12 00:19:49.245342

"""

# revision identifiers, used by Alembic.
revision = '5a7a0783e30'
down_revision = '48c16211f99'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import re
import datetime as dt


Base = declarative_base()
Session = sessionmaker()


class Examination(Base):
    __tablename__ = 'examination'

    id = sa.Column(sa.Integer, primary_key=True)

    comment = sa.Column(sa.String(128))
    date = sa.Column(sa.Date)

    def __init__(self, comment, date):
        self.comment = comment
        self.date = date

DATE_1_REGEX = re.compile(r"\d\d-\d\d-\d\d\d\d")
DATE_2_REGEX = re.compile(r"(\d\d?)\s+([a-zA-Z]+)\s+((?:\d\d)?\d\d)")

DUTCH_MONTHS = [
    'januari',
    'februari',
    'maart',
    'april',
    'mei',
    'juni',
    'juli',
    'augustus',
    'september',
    'oktober',
    'november',
    'december'
]

ENGLISH_MONTHS = [
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december'
]


def parse_date_type2(m):
    month_name = m.group(2).lower()

    try:
        month = DUTCH_MONTHS.index(month_name) + 1
    except ValueError:
        try:
            month = ENGLISH_MONTHS.index(month_name) + 1
        except ValueError:
            raise ValueError("Invalid month: {}".format(month_name))

    day = int(m.group(1))
    year = int(m.group(3))
    if year < 100:
        year += 2000

    return dt.date(year, month, day)


def upgrade():
    op.add_column('examination', sa.Column('date', sa.Date(), nullable=True))
    op.alter_column('examination', 'title', new_column_name='comment',
                    existing_type=sa.String(length=128))

    bind = op.get_bind()
    session = Session(bind=bind)

    for examination in session.query(Examination):
        datestr = examination.comment.strip()

        failed = False
        try:
            # Try 1: 20-07-2015
            if DATE_1_REGEX.match(datestr):
                date = dt.datetime.strptime(datestr, "%d-%m-%Y").date()
            else:

                # Try 2: 20 juli 2015 / 20 july 2015
                m = DATE_2_REGEX.match(datestr)
                if m:
                    date = parse_date_type2(m)
                else:
                    failed = True
        except:
            failed = True

        if not failed:
            # If we cannot parse it, just leave the string in the comment field
            # Otherwise, set the date field and set the comment field to NULL
            examination.date = date
            examination.comment = None

    session.commit()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    for examination in session.query(Examination):
        if examination.date:
            # Put the date in the old title field
            datestr = examination.date.strftime('%d-%m-%Y')
            if examination.comment is None or examination.comment == "":
                examination.comment = datestr
            else:
                examination.comment = "{} - {}".format(
                    datestr, examination.comment)

    session.commit()

    op.alter_column('examination', 'comment', new_column_name='title',
                    existing_type=sa.String(length=128))
    op.drop_column('examination', 'date')
