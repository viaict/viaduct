from sqlalchemy import event, orm

from app import db, get_locale
from app.models.base_model import BaseEntity


class NavigationEntry(db.Model, BaseEntity):
    __tablename__ = 'nagivation_entry'

    prints = ('id', 'parent_id', 'nl_title', 'en_title', 'url', 'external')

    parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    nl_title = db.Column(db.String(256))
    en_title = db.Column(db.String(256))
    url = db.Column(db.String(256))
    external = db.Column(db.Boolean)
    activity_list = db.Column(db.Boolean)
    position = db.Column(db.Integer)
    order_children_alphabetically = db.Column(db.Boolean(), default=False,
                                              nullable=False)

    parent = db.relationship(
        'NavigationEntry', remote_side='NavigationEntry.id',
        primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
        backref=db.backref('children', lazy='dynamic',
                           order_by='NavigationEntry.position'))

    page = db.relationship('Page', backref=db.backref('navigation_entry',
                                                      lazy='joined'),
                           lazy='joined')

    @orm.reconstructor
    def orm_init(self):
        self.children_fast = []

    def __init__(self, parent, nl_title, en_title, url, page_id, external,
                 activity_list, position, subtitle=None):
        if parent:
            self.parent_id = parent.id

        self.title = None
        self.nl_title = nl_title
        self.en_title = en_title
        self.url = url
        self.page_id = page_id
        self.external = external
        self.activity_list = activity_list
        self.position = position
        self.subtitle = subtitle
        self.children_fast = []
        set_navigation_entry_locale(self, None)

    def get_children(self):
        if self.order_children_alphabetically:
            return sorted(self.children_fast, key=lambda x: x.title)
        else:
            return self.children_fast

    @property
    def href(self):
        if self.external and self.url:
            return 'https://' + self.url
        else:
            return self.url if self.url else '/' + self.page.path


@event.listens_for(NavigationEntry, 'load')
def set_navigation_entry_locale(nav_entry, context):
    """
    Fill model content according to language.

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
