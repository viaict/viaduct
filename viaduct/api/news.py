from viaduct.models import NewsRevision


def get_page(item_id):
    """Get a news item's page object from its item id."""
    revision = NewsRevision.query\
        .filter(NewsRevision.item_id == item_id)\
        .first()

    return revision.page
