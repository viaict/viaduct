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
