from datetime import date
from sqlalchemy import event

from flask import url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user

from app import db, get_locale
from app.models import BaseEntity


class News(db.Model, BaseEntity):
    __tablename__ = 'news'

    nl_title = db.Column(db.String(256))
    en_title = db.Column(db.String(256))
    nl_content = db.Column(db.Text)
    en_content = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('news', lazy='dynamic'))
    needs_paid = db.Column(db.Boolean, default=False, nullable=False)

    publish_date = db.Column(db.Date)
    archive_date = db.Column(db.Date)

    def __init__(self, nl_title='', nl_content='', en_title='', en_content='',
                 user_id=None, archive_date=None, publish_date=None):

        self.title = None
        self.content = None
        self.nl_title = nl_title
        self.nl_content = nl_content
        self.en_title = en_title
        self.en_content = en_content

        self.user_id = user_id
        self.archive_date = archive_date
        if publish_date:
            self.publish_date = publish_date
        else:
            self.publish_date = date.today()

    def can_read(self, user=current_user):
        return not self.needs_paid or user.has_paid

    def get_short_content(self, characters):
        """Get a shortened version of the total post."""
        if not self.can_read():
            return _('Valid membership is required to read this news article')

        if len(self.content) > characters:
            short_content = self.content[:characters].strip()

            # Remove the last word
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '<br/><small><a href="' +\
                url_for('news.view', news_id=self.id) +\
                '">(' + _('Read more') + '...)</a></small>'

        return self.content

    def get_localized_title_content(self, locale=None):
        if not locale:
            locale = get_locale()

        nl_available = self.nl_title and self.nl_content
        en_available = self.en_title and self.en_content
        if locale == 'nl' and nl_available:
            title = self.nl_title
            content = self.nl_content
        elif locale == 'en' and en_available:
            title = self.en_title
            content = self.en_content
        elif nl_available:
            title = self.nl_title + " (" + _('Dutch') + ")"
            content = self.nl_content
        elif en_available:
            title = self.en_title + " (" + _('English') + ")"
            content = self.en_content
        else:
            title = 'N/A'
            content = 'N/A'

        return title, content


@event.listens_for(News, 'load')
def set_news_locale(news, context):
    """
    Fill model content according to language.

    This function is called after an News model is filled with data from
    the database, but before is used in all other code.

    Use the locale of the current user/client to determine which language to
    display on the whole website. If the users locale is unavailable, select
    the alternative language, suffixing the title of the news with the
    displayed language.
    """

    news.title, news.content = news.get_localized_title_content()
