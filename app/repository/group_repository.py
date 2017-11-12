from app import db
from app.models.group import Group


def find_by_id(group_id):
    return db.session.query(Group).filter_by(id=group_id).one_or_none()
