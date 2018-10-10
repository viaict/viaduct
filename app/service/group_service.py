from typing import List

from app.exceptions.base import ResourceNotFoundException, \
    AuthorizationException
from app.models.group import Group
from app.repository import group_repository
from . import user_service


def find_group_by_id(group_id: int) -> Group:
    return group_repository.find_by_id(group_id)


def get_group_by_id(group_id: int) -> Group:
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


def paginated_search_group_users(group_id: int, search: str, page: int):
    return group_repository.paginated_search_group_users(
        group_id=group_id, search=search, page=page)


def get_group_users(group_id: int):
    return group_repository.get_group_users(group_id)


def check_user_member_of_group(user, group_id):
    if user_member_of_group(user, group_id):
        return
    raise AuthorizationException(f"User not in group identified by {group_id}")


def user_member_of_group(user, group_id):
    if not group_id:
        return False

    group = group_repository.find_by_id(group_id)
    group_users = get_group_users(group_id)
    if group and user in group_users:
        return True
    else:
        return False


def remove_group_users(group_id: int, user_ids: List[int]) -> None:
    group_users = get_group_users(group_id)

    users = [user_service.get_user_by_id(user_id) for user_id in user_ids]

    for user in users:
        if user not in group_users:
            raise ResourceNotFoundException("user in group", user.id)

    group_repository.remove_group_users(group_id, user_ids)


def add_group_users(group_id: int, user_ids: List[int]) -> None:
    group = get_group_by_id(group_id)
    print(user_ids)
    users = [user_service.get_user_by_id(user_id) for user_id in user_ids]

    for user in users:
        # TODO move to repository call and delete Group.add_user(user: User)
        group.add_user(user)

    group_repository.add_group_users(group, user_ids)
