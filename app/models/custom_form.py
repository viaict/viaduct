from collections import OrderedDict

import re
from datetime import datetime
from flask import url_for
from flask_login import current_user

from app import db
from app.models.activity import Activity
from app.models.base_model import BaseEntity
from app.models.page import PageRevision, Page
from app.models.user import User
from app.service import page_service
from app.utils.google import send_email


class CustomForm(db.Model, BaseEntity):
    """
    Custom form model.

    A custom form is a form on which users can register themselves
    (see CustomFormResult) and can be bound to activities.
    """

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

    name = db.Column(db.String(256))
    origin = db.Column(db.String(4096))
    html = db.Column(db.UnicodeText())
    msg_success = db.Column(db.String(2048))
    max_attendants = db.Column(db.Integer)
    introductions = db.Column(db.Integer)
    price = db.Column(db.Float, default=0)
    terms = db.Column(db.Text())

    archived = db.Column(db.Boolean)
    requires_direct_payment = db.Column(db.Boolean, default=False,
                                        nullable=False)

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
        }), ('has_paid', {
            'label': 'Heeft betaald',
            'export': lambda r: r.has_paid,
            'on_by_default': True,
        }), ('form', {
            'label': 'Form resultaat',
            'export': lambda r: re.sub(r'%[0-9A-F]{2}', '', r.data),
            'on_by_default': False,
        }), ('introductions', {
            'label': 'Introducees',
            'export': lambda r: r.introductions,
            'on_by_default': True,
        })])

    def __init__(self, owner_id=None, name="", origin="", html="",
                 msg_success="", max_attendants=150, introductions=0,
                 terms=""):
        self.owner_id = owner_id
        self.name = name
        self.origin = origin
        self.html = html
        self.msg_success = msg_success
        self.max_attendants = max_attendants
        self.introductions = introductions
        self.terms = terms
        self.archived = False

    def has_activity(self):
        return (self.activities.count() > 0)

    def get_closest_activity(self):
        return (self.activities
                .order_by(Activity.modified.desc())
                .first())

    def submittable_by(self, user=current_user):
        # Test if the form is accessable through an activity.
        if self.has_activity() and user.is_authenticated:
            return True

        # Query all the page's this form is attached to.
        pages = Page.query.join(PageRevision, CustomForm)\
            .filter(Page.id == PageRevision.page_id)\
            .filter(PageRevision.custom_form_id == self.id).all()

        # Test if we are allowed to read on any on these pages.
        if any([page_service.can_user_read_page(page, user)
                for page in pages]):
            return True

        return False

    def is_archived(self):
        if self.archived:
            return True

        latest_activity = \
            self.activities.order_by(Activity.end_time.desc()).first()
        if latest_activity:
            return datetime.now() > latest_activity.end_time
        else:
            False

    @property
    def attendants(self):
        return sum(entry.introductions + 1 for entry in
                   self.custom_form_results.all())

    @classmethod
    def aslist(cls, current=None):
        from app.service import custom_form_service

        lst = [('Gevolgde formulieren',
                custom_form_service.
                get_active_followed_forms_by_user(current_user)),
               ('Actieve formulieren',
                custom_form_service.
                get_active_unfollowed_by_user(current_user))]

        if current is not None:
            cf = cls.query.get(current)

            if cf is not None and cf.is_archived():
                lst.append(('Gearchiveerd geselecteerd formulier', [cf]))

        return lst


class CustomFormResult(db.Model, BaseEntity):
    """
    Custom form results model.

    The custom form results are the registrations of users on custom forms.
    """

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))
    data = db.Column(db.String(4096))
    has_paid = db.Column(db.Boolean)
    introductions = db.Column(db.Integer)

    owner = db.relationship('User', backref=db.backref('custom_form_results',
                                                       lazy='dynamic'))
    form = db.relationship('CustomForm',
                           backref=db.backref('custom_form_results',
                                              lazy='dynamic'))

    def __init__(self, owner_id=None, form_id=None, data="", has_paid=False,
                 introductions=0, price=0.0):
        self.owner_id = owner_id
        self.form_id = form_id
        self.data = data
        self.has_paid = has_paid
        self.introductions = introductions
        self.price = price
        self.notify_followers()

    def __repr__(self):
        return "<FormResult owner:%s has_paid:%s>" % (self.owner.first_name,
                                                      self.has_paid)

    def notify_followers(self):
        form_url = url_for('custom_form.view_single', form_id=self.form_id,
                           _external=True)
        followers = CustomFormFollower.query\
            .filter(CustomFormFollower.form_id == self.form_id)
        owner = User.query.get(self.owner_id)
        form = CustomForm.query.get(self.form_id)
        for follower in followers:
            send_email(to=follower.owner.email,
                       subject='Formulier ingevuld',
                       email_template='email/form.html',
                       email_template_kwargs=dict(
                           sender='via',
                           user=follower.owner,
                           form_url=form_url,
                           owner=owner.first_name + " " + owner.last_name,
                           form=form.name)
                       )


class CustomFormFollower(db.Model, BaseEntity):
    prints = ('owner_id', 'form_id')

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User')

    # TODO Actually add the foreign key to the database.
    form_id = db.Column(db.Integer, db.ForeignKey('custom_form.id'))
    form = db.relationship('CustomForm')
