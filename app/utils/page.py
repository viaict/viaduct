from flask_login import current_user

from app import db
from app.models.page import Page, PagePermission


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
        return (PagePermission.get_user_rights(current_user, page) >=
                PagePermission.Level.read)

    @staticmethod
    def can_write(page):
        return (PagePermission.get_user_rights(current_user, page) >=
                PagePermission.Level.write)
