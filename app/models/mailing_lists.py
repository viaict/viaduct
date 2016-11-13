from app import db
from app.models import BaseEntity


class MailingList(db.Model, BaseEntity):

    name = db.Column(db.String(64))  # display name
    copernica_db_id = db.Column(db.Integer())
    active = db.column(db.Boolean())
    member_only = db.column(db.Boolean())

    def __init__(self, name="", db_id=0,
                 active=False, member_only=True):
        self.name = name
        self.copernica_db_id = db_id
        self.active = active
        self.member_only = member_only


class MailingListUser(db.Model, BaseEntity):

    prints = ('user_id', 'mailing_list_id', 'copernica_id', 'subscribed')

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User',
                           backref=db.backref('mailinglists',
                                              lazy='dynamic'))
    mailing_list_id = db.Column(db.Integer(),
                                db.ForeignKey('mailing_list.copernica_db_id'))
    mailing_list = db.relationship('MailingList',
                                   backref=db.backref('followers',
                                                      lazy='dynamic'))
    copernica_user_id = db.Column(db.Integer())
    subscribed = db.Column(db.Boolean(), default=False)

    def __init__(self, user_id=0, mailing_list_id=0,
                 copernica_id=0, subscribed=False):
        self.user_id = user_id
        self.mailing_list_id = mailing_list_id
        self.copernica_id = copernica_id
        self.subscribed = subscribed
