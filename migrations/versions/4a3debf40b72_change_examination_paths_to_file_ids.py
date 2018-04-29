"""Change examination paths to file ids.

Revision ID: 4a3debf40b72
Revises: adbd033b0dcd
Create Date: 2018-03-11 21:32:04.522634

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from app import app, hashfs
from app.models.examination import Examination
from app.models.base_model import BaseEntity
from app.enums import FileCategory

import os
import traceback
import re

# revision identifiers, used by Alembic.
revision = '4a3debf40b72'
down_revision = 'adbd033b0dcd'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
db = sa
db.Model = Base
db.relationship = relationship


class File(db.Model, BaseEntity):
    __tablename__ = 'file'

    hash = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20), nullable=False)

    category = db.Column(db.Enum(FileCategory), nullable=False)
    display_name = db.Column(db.String(200))


class IntermediateExamination(db.Model, BaseEntity):
    __tablename__ = 'examination'

    examination_file_id = db.Column(db.Integer, db.ForeignKey('file.id'),
                                    nullable=False)
    answers_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    examination_file = db.relationship(
        File, foreign_keys=[examination_file_id], lazy='joined')
    answers_file = db.relationship(
        File, foreign_keys=[answers_file_id], lazy='joined')

    path = db.Column(db.String(256))
    answer_path = db.Column(db.String(256))


filename_regex = re.compile(r'(.+)\.([^\s.]+)')


def migrate_single_file(path, fn):
    if not os.path.isfile(path):
        if fn != '1':
            print("File does not exist:", path)
        return None

    with open(path, 'rb') as file_reader:
        address = hashfs.put(file_reader)

    f = File()

    f.category = FileCategory.EXAMINATION
    f.hash = address.id

    m = filename_regex.match(fn)
    if m is not None:
        f.extension = m.group(2).lower()
    else:
        f.extension = ""

    db.session.add(f)
    return f


def migrate_files():
    print("Migrating all examination files to HashFS")

    exams = db.session.query(IntermediateExamination).all()
    exams_dir = app.config['EXAMINATION_UPLOAD_FOLDER']

    total = len(exams)
    stepsize = 40

    has_invalid_exams = False

    dummy_file = File()
    dummy_file.hash = '0' * 64
    dummy_file.extension = 'pdf'
    dummy_file.category = FileCategory.EXAMINATION
    db.session.add(dummy_file)

    for i, exam in enumerate(exams):
        if (i + 1) % stepsize == 0:
            print("{}/{}".format(i + 1, total))

        if exam.path is None:
            continue

        path = os.path.join(exams_dir, exam.path)

        examination_file = migrate_single_file(path, exam.path)

        if examination_file is None:
            has_invalid_exams = True
            examination_file = dummy_file
            print("Setting file of exam {} to dummy file".format(
                exam.id))

        exam.examination_file = examination_file

        if exam.answer_path:
            answers_path = os.path.join(exams_dir, exam.answer_path)
            answers_file = migrate_single_file(answers_path, exam.answer_path)

            if answers_file:
                exam.answers_file = answers_file

    if not has_invalid_exams:
        db.session.expunge(dummy_file)

    db.session.commit()


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('examination', sa.Column('answers_file_id', sa.Integer(), nullable=True))
    op.add_column('examination', sa.Column('examination_file_id', sa.Integer(), nullable=False))

    try:
        migrate_files()
    except Exception as e:
        op.drop_column('examination', 'examination_file_id')
        op.drop_column('examination', 'answers_file_id')
        raise e

    op.create_foreign_key(op.f('fk_examination_examination_file_id_file'), 'examination', 'file', ['examination_file_id'], ['id'])
    op.create_foreign_key(op.f('fk_examination_answers_file_id_file'), 'examination', 'file', ['answers_file_id'], ['id'])
    op.drop_column('examination', 'path')
    op.drop_column('examination', 'answer_path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    raise Exception("Undoing this migration is impossible")

    op.add_column('examination', sa.Column('answer_path', mysql.VARCHAR(length=256), nullable=True))
    op.add_column('examination', sa.Column('path', mysql.VARCHAR(length=256), nullable=True))
    op.drop_constraint(op.f('fk_examination_answers_file_id_file'), 'examination', type_='foreignkey')
    op.drop_constraint(op.f('fk_examination_examination_file_id_file'), 'examination', type_='foreignkey')
    op.drop_column('examination', 'examination_file_id')
    op.drop_column('examination', 'answers_file_id')
    # ### end Alembic commands ###
