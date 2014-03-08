from viaduct import db
from viaduct.models import BaseEntity


class GroupPermission(db.Model, BaseEntity):
    """Modules have names, this is not stored or registered, it is simply the
    name a module uses when it checks for permissions of a certain user. In the
    future we would like that modules register themselves so we can keep track
    of modules in use by the site and perhaps make sure that names of modules
    are unique.

    This class represents a link between a group and a module (name) and adds a
    permission integer: 0 for no rights, 1 for viewing rights, 2 for edit
    rights.

    Note that if such an entry is absent we can pretend there is actually a 0
    (no rights).

    Also note that 2 naturally also means a user can view such a module.

    Finally, we might want to use enums for instead of integers for permisions,
    but right now we just do not care enough for such pretty things.
    """

    __tablename__ = 'group_permission'

    module_name = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship("Group", backref=db.backref('module_permissions',
                                                        lazy='dynamic'))
    permission = db.Column(db.Integer)

    def __init__(self, module_name, group_id, permission):
        """
        * permission: an integer; 0 for no rights, 1 for viewing rights, 2 for
            edit rights
        """
        self.module_name = module_name
        self.group_id = group_id
        self.permission = permission
