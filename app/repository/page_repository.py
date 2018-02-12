from app import db
from app.models.group import Group
from app.models.page import Page, PageReadPermission


def get_read_permission_groups_by_page(page):
    return db.session.query(Group) \
        .join(PageReadPermission) \
        .filter(PageReadPermission.page == page) \
        .all()


def add_page_group_read_permission(page, added_groups):
    permissions = [PageReadPermission(page=page, group=group)
                   for group in added_groups]
    db.session.add_all(permissions)
    db.session.commit()


def delete_page_group_read_permission(page, removed_groups):
    db.session.query(PageReadPermission).filter(
        PageReadPermission.page == page,
        PageReadPermission.group_id.in_([g.id for g in removed_groups])
    ).delete(synchronize_session='fetch')
    db.session.commit()


def get_page_by_path(path):
    return db.session.query(Page).filter(Page.path == path).first()


def delete_page(page):
    db.session.delete(page)
    db.session.commit()


def delete_read_page_permission(page):
    db.session.query(PageReadPermission).filter(
        PageReadPermission.page_id == page.id
    ).delete(synchronize_session='fetch')
    db.session.commit()
