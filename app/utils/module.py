from flask.ext.login import current_user

from app.utils.user import UserAPI
from app.models.permission import GroupPermission

import sys


def import_module(name, globals=globals(), locals=locals(), fromlist=[],
                  level=-1):
    __import__(name)

    return sys.modules[name]


class ModuleAPI:

    @staticmethod
    def can_read(module_name, needs_payed=False):
        """
        Checks if the current user can view the module_name
        Distinguishes between payed members and regular users
        """
        if needs_payed and (not current_user or not current_user.has_payed):
            return False
        return ModuleAPI\
            .get_highest_permission_for_module(module_name) >= 1

    @staticmethod
    def can_write(module_name, needs_payed=False):
        """
        Checks if the current user can edit the module_name
        """
        if needs_payed and (not current_user or not current_user.has_payed):
            return False
        return ModuleAPI\
            .get_highest_permission_for_module(module_name) >= 2

    @staticmethod
    def get_highest_permission_for_module(module_name):
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
