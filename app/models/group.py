# To prevent circular dependencies with page and committee,
# CommitteeRevison must be imported inside functions
from app import db
from app.models.base_model import BaseEntity
from app.utils import google


class UserGroup(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        primary_key=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'),
                         primary_key=True, nullable=False)


class Group(db.Model, BaseEntity):
    prints = ('id', 'name')

    name = db.Column(db.String(200), unique=True)

    users = db.relationship('User', secondary='user_group',
                            backref=db.backref('groups', lazy='joined',
                                               order_by='Group.name'),
                            lazy='dynamic')

    mailtype = db.Column(db.Enum('none', 'mailinglist', 'mailbox',
                                 name='group_mailing_type'),
                         nullable=False)
    maillist = db.Column(db.String(100), unique=True)

    def __init__(self, name, maillist=None, mailtype=None):
        self.name = name
        if maillist is None:
            self.mailtype = 'none'
        else:
            if not (mailtype == 'mailinglist' or mailtype == 'mailbox'):
                raise ValueError(
                    'When maillist is set, mailtype must be either '
                    '\'mailinglist\' or \'mailbox\'')

            self.maillist = maillist
            self.mailtype = mailtype

    def is_committee(self, id):
        from app.models.committee import CommitteeRevision
        u = db.session.query(CommitteeRevision)\
              .filter(CommitteeRevision.group_id == id)
        return db.session.query(u.exists()).first()[0]

    def has_user(self, user):
        if not user:
            return False
        else:
            return self.users.filter(UserGroup.user_id == user.id)\
                .count() > 0

    def add_user(self, user):
        if not self.has_user(user):
            self.add_email_to_maillist(user.email)
            self.users.append(user)
            return self

    def add_email_to_maillist(self, email):
        if self.mailtype == 'mailinglist':
            google.add_email_to_group_if_not_exists(email, self.maillist)
        elif self.mailtype == 'mailbox':
            google.add_email_to_group_if_not_exists(
                email, 'list-' + self.maillist)

    def remove_email_from_maillist(self, email):
        if self.mailtype == 'mailinglist':
            google.remove_email_from_group_if_exists(email, self.maillist)
        elif self.mailtype == 'mailbox':
            google.remove_email_from_group_if_exists(
                email, 'list-' + self.maillist)

    def delete_user(self, user):
        if self.has_user(user):
            self.remove_email_from_maillist(user.email)
            if self.is_committee(self.id):
                google.add_email_to_group_if_not_exists(user.email, "aal")
            self.users.remove(user)

    def get_users(self):
        # FIXME: backwards compatibility.
        return self.users

    def remove_members_from_maillist(self):
        for user in self.users:
            self.remove_email_from_maillist(user.email)

    def add_members_to_maillist(self):
        for user in self.users:
            self.add_email_to_maillist(user.email)
