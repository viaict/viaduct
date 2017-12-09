from app.models.group import Group


def find_group_by_id(group_id):
    return Group.query.filter(Group.id == group_id).one_or_none()
