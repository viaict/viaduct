from viaduct import db
from viaduct.models import BaseEntity


class NavigationEntry(db.Model, BaseEntity):
    __tablename__ = 'nagivation_entry'

    prints = ('id', 'parent_id', 'title', 'url', 'external')

    parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
    title = db.Column(db.String(256))
    url = db.Column(db.String(256))
    external = db.Column(db.Boolean)
    activity_list = db.Column(db.Boolean)
    position = db.Column(db.Integer)

    parent = db.relationship(
        'NavigationEntry', remote_side='NavigationEntry.id',
        primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
        backref=db.backref('children', lazy='dynamic'))

    def __init__(self, parent, title, url, external, activity_list, position, subtitle=None):
        if parent:
            self.parent_id = parent.id

        self.title = title
        self.url = url
        self.external = external
        self.activity_list = activity_list
        self.position = position
        self.subtitle = subtitle

    def get_children(self, ordered=True):
        childs = self.children
        if ordered == True:
            childs = childs.order_by(NavigationEntry.position)
        return childs
