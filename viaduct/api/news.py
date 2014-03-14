from viaduct.models import NewsRevision


def get_latest_revision(instance_id):
    """Get a news item's page object from its item id."""
    return NewsRevision.get_query()\
        .filter(NewsRevision.instance_id == instance_id)\
        .first()
