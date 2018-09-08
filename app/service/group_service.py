from app.exceptions import ResourceNotFoundException
from app.models.group import Group
from app.repository import group_repository


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
