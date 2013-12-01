from flask.ext.login import current_user
from viaduct.models.page import Page, PagePermission

from viaduct import db

from flask import request, url_for

from viaduct.models.group import Group

class PageAPI:
    @staticmethod
    def remove_page(path):
        page = Page.query.filter(Page.path==path).first()

        if not page:
            return False

        for rev in page.revisions.all():
            db.session.delete(rev)
        db.session.delete(page)

        db.session.commit()

        return True
