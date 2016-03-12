from app import db
from app.models import BaseEntity, Activity, Transaction

from collections import OrderedDict


def export_form_data(r):
    import re
    return re.sub(r'%[0-9A-F]{2}', '', r.data)


class CustomForm(db.Model, BaseEntity):
    __tablename__ = 'custom_form'

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(256))
    origin = db.Column(db.String(4096))
    html = db.Column(db.UnicodeText())
    msg_success = db.Column(db.String(2048))
    max_attendants = db.Column(db.Integer)
    price = db.Column(db.Float, default=0)
    owner = db.relationship('User', backref=db.backref('custom_forms',
                                                       lazy='dynamic'))
    terms = db.Column(db.String(4096))
    transaction_description = db.Column(db.String(256))

    archived = db.Column(db.Boolean)

    exports = \
        OrderedDict([('user_id', {
            'label': 'Gebruiker ID',
            'export': lambda r: r.owner_id,
            'on_by_default': False,
        }), ('user_email', {
            'label': 'Gebruiker email',
            'export': lambda r: r.owner.email,
            'on_by_default': True,
        }), ('user_name', {
            'label': 'Gebruiker naam',
            'export': lambda r: '%s %s' % (r.owner.first_name,
                                           r.owner.last_name),
            'on_by_default': True,
        }), ('date', {
            'label': 'Inschrijfdatum',
            'export': lambda r: r.created,
            'on_by_default': False,
        }), ('has_payed', {
            'label': 'Heeft betaald',
            'export': lambda r: r.has_payed,
            'on_by_default': True,
        }), ('form', {
            'label': 'Form resultaat',
            'export': export_form_data,
            'on_by_default': False,
        })])

    def __init__(self, owner_id=None, name="", origin="", html="",
                 msg_success="", max_attendants=150, terms=""):
        self.owner_id = owner_id
        self.name = name
        self.origin = origin
        self.html = html
        self.msg_success = msg_success
        self.max_attendants = max_attendants
        self.terms = terms
        self.archived = False

    def has_activity(self):
        return (self.activities.count() > 0)

    def get_closest_activity(self):
        return (self.activities
                .order_by(Activity.modified.desc())
                .first())

    def update_payment(transaction_id, payed):
        transaction = (Transaction.query
                       .filter(Transaction.id == transaction_id)
                       .first())
        if transaction.form_result:
            transaction.form_result.has_payed = payed
            db.session.commit()


class CustomFormResult(db.Model, BaseEntity):
    __tablename__ = 'custom_form_result'

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))
    data = db.Column(db.String(4096))
    has_payed = db.Column(db.Boolean)

    owner = db.relationship('User', backref=db.backref('custom_form_results',
                                                       lazy='dynamic'))
    form = db.relationship('CustomForm',
                           backref=db.backref('custom_form_results',
                                              lazy='dynamic'))

    def __init__(self, owner_id=None, form_id=None, data="", has_payed=False,
                 price=0.0):
        self.owner_id = owner_id
        self.form_id = form_id
        self.data = data
        self.has_payed = has_payed
        self.price = price

    def __repr__(self):
        return "<FormResult owner:%s has_payed:%s>" % (self.owner.first_name,
                                                       self.has_payed)


class CustomFormFollower(db.Model, BaseEntity):
    __tablename__ = 'custom_form_follower'

    prints = ('owner_id', 'form_id')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    form_id = db.Column(db.Integer)

    owner = db.relationship(
        'User', backref=db.backref('custom_forms_following', lazy='dynamic'))

    def __init__(self, owner_id=None, form_id=None):
        self.owner_id = owner_id
        self.form_id = form_id