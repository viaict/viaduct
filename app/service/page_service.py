from app.repository import page_repository
from app.service import group_service


def set_read_page_permissions(page, new_groups):
    current_groups = set(get_read_permission_groups_by_page(page))
    new_groups = set(new_groups)

    added_groups = new_groups - current_groups
    removed_groups = current_groups - new_groups

    if added_groups:
        page_repository.add_page_group_read_permission(page, added_groups)
    if removed_groups:
        page_repository.delete_page_group_read_permission(page, removed_groups)


def get_read_permission_groups_by_page(page):
    return page_repository.get_read_permission_groups_by_page(page)


def can_user_read_page(page, user):
    """If the page needs membership, the user has_paid has to be true."""
    matched_paid = not page.needs_paid or user.has_paid

    # If page has custom permission
    if page.custom_read_permission:
        user_groups = set(group_service.get_group_for_user(user))
        page_read_groups = set(get_read_permission_groups_by_page(page))
        if not user_groups.intersection(page_read_groups):
            return False
    return matched_paid


def get_page_by_path(path):
    return page_repository.get_page_by_path(path)


def delete_page_by_path(path):
    page = page_repository.get_page_by_path(path)
    if not page:
        return False
    else:
        page_repository.delete_page(page)
    return True


def delete_read_page_permission(page):
    page_repository.delete_read_page_permission(page)
