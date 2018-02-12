from app import db
from app.models.group import Group, user_group


def find_by_id(group_id):
    return db.session.query(Group).filter_by(id=group_id).one_or_none()


def find_groups():
    return db.session.query(Group).order_by(Group.name).all()


def get_group_for_user(user):
    # return user.groups
    return db.session.query(Group) \
        .join(user_group) \
        .filter(user_group.user_id == user.id) \
        .all()
