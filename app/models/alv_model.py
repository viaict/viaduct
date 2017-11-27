from sqlalchemy import event

from app import db, get_locale
from app.models.base_model import BaseEntity


class Alv(db.Model, BaseEntity):
    nl_name = db.Column(db.String(128))
    en_name = db.Column(db.String(128))

    date = db.Column(db.Date, nullable=False)

    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'),
                            nullable=True)
    activity = db.relationship('Activity')

    chairman_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chairman = db.relationship('User', foreign_keys=[chairman_user_id])

    secretary_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    secretary = db.relationship('User', foreign_keys=[secretary_user_id])

    minutes_file_id = db.Column(db.Integer, db.ForeignKey('file.id'),
                                nullable=True)
    minutes_file = db.relationship('File')

    @property
    def presidium(self):
        from app.service import alv_service
        return alv_service.format_presidium(self)

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
        elif locale == 'en' and self.en_name:
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
