import logging

from app import db, Roles
from app.models.group import Group
from app.models.role_model import GroupRole
from app.models.user import User

_logger = logging.getLogger(__name__)


def load_user_roles(user_id):
    roles = db.session.query(GroupRole.role). \
        join(GroupRole.group, Group.users). \
        filter(User.id == user_id).group_by(GroupRole.role).all()
    return [Roles[role.role] for role in roles]


def find_all_roles_by_group_id(group_id):
    roles = db.session.query(GroupRole) \
        .filter(GroupRole.group_id == group_id) \
        .order_by(GroupRole.role).all()
    return [Roles[role.role] for role in roles]


def delete_roles_by_group(group_id, removed_roles):
    roles = [role.value for role in removed_roles]
    db.session.query(GroupRole).filter(
        GroupRole.group_id == group_id,
        GroupRole.role.in_(roles)
    ).delete(synchronize_session='fetch')


def insert_roles_by_group(group_id, added_roles):
    roles = []
    for role in added_roles:
        group_role = GroupRole()
        group_role.group_id = group_id
        group_role.role = role.name
        roles.append(group_role)

    db.session.add_all(roles)
    db.session.commit()
