# To prevent circular dependencies with page and committee,
# CommitteeRevison must be imported inside functions
from app import db
from app.models.base_model import BaseEntity
from app.utils import google

user_group = db.Table(
    'user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Group(db.Model, BaseEntity):
    __tablename__ = 'group'

    prints = ('id', 'name')

    name = db.Column(db.String(200), unique=True)

    users = db.relationship('User', secondary=user_group,
                            backref=db.backref('groups', lazy='joined',
                                               order_by='Group.name'),
                            lazy='dynamic')

    maillist = db.Column(db.String(100), unique=True)

    def __init__(self, name, maillist):
        self.name = name
        self.maillist = maillist

    def __str__(self):
        return self.name

    def is_committee(self, id):
        from app.models.committee import CommitteeRevision
        u = db.session.query(CommitteeRevision)\
              .filter(CommitteeRevision.group_id == id)
        return db.session.query(u.exists()).first()[0]

    def has_user(self, user):
        if not user:
            return False
        else:
            return self.users.filter(user_group.c.user_id == user.id)\
                .count() > 0

    def add_user(self, user):
        if not self.has_user(user):
            self.add_email_to_maillist(user.email)
            self.users.append(user)
            return self

    def add_email_to_maillist(self, email):
        if self.maillist:
            google.add_email_to_group_if_not_exists(email, self.maillist)

    def remove_email_from_maillist(self, email):
        if self.maillist:
            google.remove_email_from_group_if_exists(email, self.maillist)

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
