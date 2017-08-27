from sqlalchemy import event

from app import db, get_locale
from app.models.page import SuperRevision
from app.models.user import User

from flask_babel import lazy_gettext as _


class CommitteeRevision(SuperRevision):
    __tablename__ = 'committee_revision'

    prints = ('id', 'title', 'group_id', 'coordinator_id', 'interim',
              'open_new_members')
    context = {'User': User}

    nl_description = db.Column(db.Text)
    en_description = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    coordinator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    interim = db.Column(db.Boolean)
    open_new_members = db.Column(db.Boolean, nullable=False, default=0)

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

    def __init__(self, page=None, nl_title='', en_title='', comment='',
                 user_id=None, nl_description='', en_description='',
                 group_id=None, coordinator_id=None, interim=None,
                 open_new_members=False):
        super(CommitteeRevision, self).__init__(nl_title, en_title, comment)

        self.page = page
        self.user_id = user_id

        self.description = None
        self.nl_description = nl_description
        self.en_description = en_description
        self.group_id = group_id
        self.coordinator_id = coordinator_id
        self.interim = interim
        self.open_new_members = open_new_members

    def get_comparable(self):
        return self.description


@event.listens_for(CommitteeRevision, 'load')
def set_committee_revision_locale(com_rev, context):
    """
    Fill model content according to language.

    This function is called after an CommitteeRevision model is filled with
    data from the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """
    locale = get_locale()
    nl_available = com_rev.nl_title and com_rev.nl_description
    en_available = com_rev.en_title and com_rev.en_description
    if locale == 'nl' and nl_available:
        com_rev.title = com_rev.nl_title
        com_rev.description = com_rev.nl_description
    elif locale == 'en' and en_available:
        com_rev.title = com_rev.en_title
        com_rev.description = com_rev.en_description
    elif nl_available:
        com_rev.title = com_rev.nl_title + " (" + _('Dutch') + ")"
        com_rev.description = com_rev.nl_description
    elif en_available:
        com_rev.title = com_rev.en_title + " (" + _('English') + ")"
        com_rev.description = com_rev.en_description
    else:
        com_rev.title = 'N/A'
        com_rev.description = 'N/A'
