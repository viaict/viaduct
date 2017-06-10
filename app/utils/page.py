from flask_login import current_user
from app.models.page import Page, PagePermission

from app import db


class PageAPI:
    @staticmethod
    def remove_page(path):
        page = Page.get_by_path(path)
        if not page:
            return False

        db.session.delete(page)
        db.session.commit()

        return True

    @staticmethod
    def can_read(page):
        if page.needs_paid and (current_user.is_anonymous or
                                not current_user.has_paid):
            return False

        return PagePermission.get_user_rights(current_user, page) > 0

    @staticmethod
    def can_write(page):
        return PagePermission.get_user_rights(current_user, page) > 1
