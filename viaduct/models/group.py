from viaduct import db
from viaduct.models import BaseEntity

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
                            backref=db.backref('groups', lazy='dynamic'),
                            lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def has_user(self, user):
        if not user:
            return False
        else:
            return self.users.filter(user_group.c.user_id == user.id)\
                .count() > 0

    def add_user(self, user):
        if not self.has_user(user):
            self.users.append(user)

            return self

    def delete_user(self, user):
        if self.has_user(user):
            self.users.remove(user)

    def get_users(self):
        # FIXME: backwards compatibility.
        return self.users
