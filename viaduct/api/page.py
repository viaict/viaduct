from flask.ext.login import current_user
from viaduct.models.page import Page, PagePermission, PageRevision

from viaduct import db

from flask import render_template


class PageAPI:
    @staticmethod
    def remove_page(path):
        page = Page.query.filter(Page.path == path).first()

        if not page:
            return False

        for rev in page.revisions.all():
            db.session.delete(rev)
        for perm in page.permissions.all():
            db.session.delete(perm)
        db.session.commit()

        db.session.delete(page)
        db.session.commit()

        return True

    @staticmethod
    def get_footer():
        footer = Page.query.filter(Page.path == 'footer').first()

        if not footer:
            footer = Page('footer')

        revision = footer.get_latest_revision()

        if revision:
            exists = True
        else:
            revision = PageRevision(footer, 'Footer', '', current_user,
                                    '<strong>No footer found</strong>')
            exists = False

        return render_template('page/get_footer.htm', footer_revision=revision,
                               footer=footer, exists=exists)
