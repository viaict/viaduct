from app import db
from app.models.group import Group
from app.models.page import PagePermission


def get_permission_groups_by_page(page, permission_type):
    return db.session.query(Group) \
        .join(PagePermission) \
        .filter(PagePermission.permission == permission_type,
                PagePermission.page == page) \
        .all()


def add_page_group_permission(page, added_groups, permission):
    permissions = [PagePermission(page=page, group=group,
                                  permission=permission)
                   for group in added_groups]
    db.session.add_all(permissions)
    db.session.commit()


def delete_page_group_permission(page, removed_groups, permission):
    db.session.query(PagePermission).filter(
        PagePermission.page == page,
        PagePermission.group_id.in_([g.id for g in removed_groups]),
        PagePermission.permission == permission
    ).delete(synchronize_session='fetch')
    db.session.commit()
