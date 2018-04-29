import logging

from flask_login import current_user

from app import app
from app.repository import role_repository
from flask import request

_logger = logging.getLogger(__name__)


def user_has_role(user, *roles):
    return all(role in user.roles for role in roles)


def find_all_roles_by_group_id(group_id):
    return role_repository.find_all_roles_by_group_id(group_id)


@app.before_request
def load_user_roles():
    if request.endpoint and not request.endpoint.startswith('static'):
        current_user.roles = role_repository.load_user_roles(current_user.id)


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
