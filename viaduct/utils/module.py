from functools import wraps
from flask import abort, session
from flask.ext.login import current_user

from viaduct.api.user import UserAPI
from viaduct.models.permission import GroupPermission


def require_read_perm(module_name, needs_payed=False):
    def real_require_read(f):
        @wraps(f)
        def df(*args, **kwargs):
            permission = highest_module_permission(module_name)
            if (needs_payed and not current_user.has_payed or permission < 1):
                session['prev'] = module_name + '.' + f.__name__
                abort(403)
            else:
                return f(*args, **kwargs)
        return df
    return real_require_read


def require_write_perm(module_name, needs_payed=False):
    def real_require_write(f):
        @wraps(f)
        def df(*args, **kwargs):
            permission = highest_module_permission(module_name)
            if (needs_payed and not current_user.has_payed or permission < 2):
                session['prev'] = module_name + '.' + f.__name__
                abort(403)
            else:
                return f(*args, **kwargs)
        return df
    return real_require_write


# def can_read(module_name, needs_payed=False): TODO: PURGE
def has_read_perm(module_name, needs_payed=False):
    """
    Checks if the current user can view the module_name
    Distinguishes between payed members and regular users
    """
    if needs_payed and (not current_user or not current_user.has_payed):
        return False
    return highest_module_permission(module_name) >= 1


# def can_write(module_name, needs_payed=False): TODO: PURGE
def has_write_perm(module_name, needs_payed=False):
    """
    Checks if the current user can edit the module_name
    """
    if needs_payed and (not current_user or not current_user.has_payed):
        return False
    return highest_module_permission(module_name) >= 2


def highest_module_permission(module_name):
    """Returns the highest permission for the current user for the given
    module name. Should crash if all has been deleted and the user is not
    logged in.

    """
    groups = UserAPI.get_groups_for_current_user()
    highest = 0

    for group in groups:
        query = GroupPermission.query\
            .filter(GroupPermission.group_id == group.id)
        query = query.filter(GroupPermission.module_name == module_name)
        matching_permissions = query.all()

        for matching_permission in matching_permissions:
            highest = matching_permission.permission if\
                matching_permission.permission > highest else highest
    return highest
