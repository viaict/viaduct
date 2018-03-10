from app import db
from app.models.file import File


def create_file():
    return File()


def save(_file):
    db.session.add(_file)
    db.session.commit()


def find_all_files():
    return db.session.query(File) \
        .order_by(File.category, File.display_name).all()


def find_all_files_by_category(category):
    return db.session.query(File) \
        .filter_by(category=category) \
        .order_by(File.display_name).all()


def find_all_files_by_hash(_hash):
    return db.session.query(File) \
        .filter_by(hash=_hash) \
        .order_by(File.category).all()


def find_file_by_id(file_id):
    return db.session.query(File) \
        .filter_by(id=file_id) \
        .one_or_none()


def find_file_by_display_name(display_name):
    return db.session.query(File) \
        .filter_by(display_name=display_name) \
        .one_or_none()


def delete(_file):
    db.session.delete(_file)
    db.session.commit()
