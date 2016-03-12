from sqlalchemy import event
from viaduct import db, get_locale
from viaduct.models import BaseEntity
from flask.ext.babel import lazy_gettext as _


class NavigationEntry(db.Model, BaseEntity):
    __tablename__ = 'nagivation_entry'

    prints = ('id', 'parent_id', 'nl_title', 'en_title', 'url', 'external')

    parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
    nl_title = db.Column(db.String(256))
    en_title = db.Column(db.String(256))
    url = db.Column(db.String(256))
    external = db.Column(db.Boolean)
    activity_list = db.Column(db.Boolean)
    position = db.Column(db.Integer)

    parent = db.relationship(
        'NavigationEntry', remote_side='NavigationEntry.id',
        primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
        backref=db.backref('children', lazy='dynamic'))

    def __init__(self, parent, nl_title, en_title, url, external,
                 activity_list, position, subtitle=None):
        if parent:
            self.parent_id = parent.id

        self.title = None
        self.nl_title = nl_title
        self.en_title = en_title
        self.url = url
        self.external = external
        self.activity_list = activity_list
        self.position = position
        self.subtitle = subtitle
        set_navigation_entry_locale(self, None)

    def get_children(self, ordered=True):
        childs = self.children
        if ordered:
            childs = childs.order_by(NavigationEntry.position)
        return childs


@event.listens_for(NavigationEntry, 'load')
def set_navigation_entry_locale(nav_entry, context):
    """
    This function is called after an NavigationEntry model is filled with data
    from the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """
    locale = get_locale()
    if locale == 'nl' and nav_entry.nl_title:
        nav_entry.title = nav_entry.nl_title
    elif locale == 'en' and nav_entry.en_title:
        nav_entry.title = nav_entry.en_title
    elif nav_entry.nl_title:
        nav_entry.title = nav_entry.nl_title
    elif nav_entry.en_title:
        nav_entry.title = nav_entry.en_title
    else:
        nav_entry.title = 'N/A'
