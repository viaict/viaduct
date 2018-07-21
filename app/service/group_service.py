from app.exceptions.base import ResourceNotFoundException, \
    AuthorizationException
from app.repository import group_repository


def get_group_by_id(group_id):
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundException("group", group_id)
    return group


def get_group_by_name(group_name):
    group = group_repository.get_group_by_name(group_name)
    if not group:
        raise ResourceNotFoundException("group", group_name)
    return group


def find_groups():
    return group_repository.find_groups()


def get_groups_for_user(user):
    return group_repository.get_groups_for_user(user)


def check_user_member_of_group(user, group_id):
    if user_member_of_group(user, group_id):
        return
    raise AuthorizationException(f"User not in group identified by {group_id}")


def user_member_of_group(user, group_id):
    if not group_id:
        return False

    group = group_repository.find_by_id(group_id)
    if group and user in group.users:
        return True
    else:
        return False
