from app.models.page import PagePermission
from app.repository import page_repository


def set_page_permissions(page, new_groups, permission_type):
    current_groups = set(get_permission_groups_by_page(page, permission_type))
    new_groups = set(new_groups)

    added_groups = new_groups - current_groups
    removed_groups = current_groups - new_groups

    if added_groups:
        page_repository.add_page_group_permission(
            page, added_groups, permission_type.value)
    if removed_groups:
        page_repository.delete_page_group_permission(
            page, removed_groups, permission_type.value)


def get_permission_groups_by_page(page, permission_type):
    return page_repository.get_permission_groups_by_page(
        page, permission_type.value)


def can_user_read_page(page, user):
    return (PagePermission.get_user_rights(user, page) >=
            PagePermission.Level.read)


def can_user_write_page(page, user):
    return (PagePermission.get_user_rights(user, page) >=
            PagePermission.Level.write)


def get_page_by_path(path):
    return page_repository.get_page_by_path(path)


def delete_page_by_path(path):
    page = page_repository.get_page_by_path(path)
    if not page:
        return False
    else:
        page_repository.delete_page(page)
    return True
