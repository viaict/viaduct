from viaduct import db
from viaduct.models.page import SuperRevision
from viaduct.models import User


class CommitteeRevision(SuperRevision):
    __tablename__ = 'committee_revision'

    prints = ('id', 'title', 'group_id', 'coordinator_id', 'interim')

    context = {'User': User}

    description = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    interim = db.Column(db.Boolean)

    # Relationships.
    group = db.relationship(
        'Group', backref=db.backref('committee_revisions', lazy='dynamic'))
    coordinator = db.relationship(
        'User', backref=db.backref('coordinator_committee_revisions',
                                   lazy='dynamic'),
        foreign_keys=[coordinator_id])

    # Necessary page columns.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

    user = db.relationship(
        'User', backref=db.backref('committee_revisions', lazy='dynamic'),
        foreign_keys=[user_id])
    page = db.relationship(
        'Page', backref=db.backref('committee_revisions', lazy='dynamic'))

    def __init__(self, page=None, title='', comment='', user_id=None,
                 description='', group_id=None, coordinator_id=None,
                 interim=None):
        super(CommitteeRevision, self).__init__(title, comment)

        self.page = page
        self.user_id = user_id

        self.description = description
        self.group_id = group_id
        self.coordinator_id = coordinator_id
        self.interim = interim

    def get_comparable(self):
        return self.description

