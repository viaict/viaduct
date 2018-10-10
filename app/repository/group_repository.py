from flask_sqlalchemy import Pagination
from sqlalchemy import or_
from typing import List

from app import db
from app.models.group import Group, UserGroup
from app.models.user import User


def find_by_id(group_id: int) -> Group:
    return db.session.query(Group).filter_by(id=group_id).one_or_none()


def get_group_by_name(group_name: str) -> Group:
    return db.session.query(Group) \
        .filter_by(name=group_name) \
        .one_or_none()


def find_groups() -> List[Group]:
    return db.session.query(Group).order_by(Group.name).all()


def get_groups_for_user(user: User) -> List[Group]:
    return db.session.query(Group) \
        .join(UserGroup) \
        .filter(UserGroup.user_id == user.id) \
        .all()


def paginated_search_group_users(group_id: int, page: int,
                                 page_size: int = 15, search: str = "") \
        -> Pagination:
    q = db.session.query(User) \
        .join(UserGroup, UserGroup.user_id == User.id) \
        .order_by(User.id.asc()) \
        .filter(UserGroup.group_id == group_id)

    if search is not "":
        q = q.filter(or_(User.email.ilike(f"%{search}%"),
                         User.first_name.ilike(f"%{search}%"),
                         User.last_name.ilike(f"%{search}%"),
                         User.student_id.ilike(f"%{search}%")))
    return q.paginate(page, page_size, False)


def get_group_users(group_id: int) -> List[User]:
    return db.session.query(User) \
        .join(UserGroup,
              UserGroup.user_id == User.id) \
        .filter(UserGroup.group_id == group_id) \
        .all()


def remove_group_users(group_id: int, user_ids: List[int]) -> None:
    db.session.query(UserGroup) \
        .filter(UserGroup.group_id == group_id,
                UserGroup.user_id.in_(user_ids)) \
        .delete(synchronize_session=False)
    db.session.commit()


def add_group_users(group: Group, user_ids: List[int]) -> None:
    # TODO Move creation of UserGroup here.
    db.session.commit()
