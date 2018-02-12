from app.exceptions import ResourceNotFoundException
from app.repository import group_repository


def get_group_by_id(group_id):
    group = group_repository.find_by_id(group_id)
    if not group:
        raise ResourceNotFoundException("group", group_id)
    return group


def find_groups():
    return group_repository.find_groups()


def get_group_for_user(user):
    return group_repository.get_group_for_user(user)
