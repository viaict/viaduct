from app.models.page import Page


def get_alphabetical():
    pages = Page.query.filter(Page.type == 'committee').all()
    revisions = [page.get_latest_revision() for page in pages]
    revisions.sort(key=lambda r: r.title)
    return revisions
