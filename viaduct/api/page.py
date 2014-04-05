from flask.ext.login import current_user
from viaduct.models.page import Page, PagePermission, PageRevision  

from viaduct import db

from flask import request, url_for, render_template

from viaduct.models.group import Group

class PageAPI:
    @staticmethod
    def remove_page(path):
        page = Page.query.filter(Page.path==path).first()

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

        if footer.revisions.count() > 0:
            revision = footer.revisions.order_by(PageRevision.id.desc()).first()
            exists = True
        else:
            revision = PageRevision(footer, current_user,
                                                '', '<b> No footer found </b>'
                                                '', True)
            exists = False

        print vars(footer)

        return render_template('page/get_footer.htm', footer_revision=revision, footer=footer, exists=exists)