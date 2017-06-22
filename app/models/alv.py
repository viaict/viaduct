from flask_babel import lazy_gettext as _
from sqlalchemy import event

from app import db, get_locale
from app.models import BaseEntity


class Alv(db.Model, BaseEntity):
    nl_name = db.Column(db.String(128))
    en_name = db.Column(db.String(128))

    date = db.Column(db.Date, nullable=False)

    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'),
                            nullable=True)

    def __str__(self):
        return '%s' % self.alv

    def format_presidium(self):
        if self.presidium:
            presidium = map(str, sorted(self.presidium, key=lambda x: x.role))
            return ', '.join(presidium)
        else:
            return _('No presidium')

    def get_localized_name(self, locale=None):
        if not locale:
            locale = get_locale()

        if locale == 'nl' and self.nl_name:
            return self.nl_name
        elif locale == 'en' and self.en_name:
            return self.en_name
        elif self.nl_name:
            return self.nl_name + " (Dutch)"
        elif self.en_name:
            return self.en_name + " (Engels)"
        else:
            return 'N/A'


class AlvPresidium(db.Model, BaseEntity):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    role = db.Column(db.Integer(), nullable=False)

    alv_id = db.Column(db.Integer(), db.ForeignKey('alv.id'))
    alv = db.relationship("Alv", backref='presidium')

    presidium_roles = {
        0: _('Chairman'),
        1: _('Secretary'),
        2: _('Other'),
    }

    def __str__(self):
        return '%s (%s)' % (self.user, self.presidium_roles[self.role])


class AlvDocument(db.Model, BaseEntity):
    nl_name = db.Column(db.String(128), nullable=False)
    en_name = db.Column(db.String(128), nullable=False)

    alv_id = db.Column(db.Integer(), db.ForeignKey('alv.id'))
    alv = db.relationship('Alv', backref='documents')

    def get_localized_name(self, locale=None):
        if not locale:
            locale = get_locale()

        if locale == 'nl' and self.nl_name:
            return self.nl_name
        elif locale == 'en' and self.name:
            return self.en_name
        elif self.nl_name:
            return self.nl_name + " (Dutch)"
        elif self.en_name:
            return self.en_name + " (Engels)"
        else:
            return 'N/A'


class AlvDocumentVersion(db.Model, BaseEntity):
    file_id = db.Column(db.Integer(), db.ForeignKey('file.id'))
    file = db.relationship('File')

    alv_document_id = db.Column(db.Integer(), db.ForeignKey('alv_document.id'))
    alv_document = db.relationship('AlvDocument', backref='versions')

    final = db.Column(db.Boolean(), nullable=False)


@event.listens_for(Alv, 'load')
def set_alv_locale(alv, context):
    """
    Fill model content according to language.

    This function is called after an Activity model is filled with data from
    the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """

    alv.name = alv.get_localized_name()


@event.listens_for(AlvDocument, 'load')
def set_alv_document_locale(alv_document, context):
    """
    Fill model content according to language.

    This function is called after an Activity model is filled with data from
    the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the activity with the
    displayed language.
    """

    alv_document.name = alv_document.get_localized_name()
