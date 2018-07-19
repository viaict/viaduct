import logging

from app.repository import role_repository

_logger = logging.getLogger(__name__)


def user_has_role(user, *roles):
    if not user:
        return False

    if user.is_authenticated:
        if user.disabled:
            return False

        user_roles = role_repository.load_user_roles(user.id)
        return all(role in user_roles for role in roles)
    else:
        return False


def find_all_roles_by_group_id(group_id):
    return role_repository.find_all_roles_by_group_id(group_id)


def get_groups_with_role(role):
    return role_repository.get_groups_with_role(role)


def set_roles_for_group(group_id, new_roles):
    """Update a groups roles, uses set theory to determine what changed."""
    current_roles = set(find_all_roles_by_group_id(group_id))
    new_roles = set(new_roles)

    removed_roles = current_roles - new_roles
    added_roles = new_roles - current_roles

    if removed_roles:
        role_repository.delete_roles_by_group(group_id, removed_roles)
    if added_roles:
        role_repository.insert_roles_by_group(group_id, added_roles)
