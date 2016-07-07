from datetime import date
from sqlalchemy import event

from flask import url_for
from flask_babel import lazy_gettext as _

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

    publish_date = db.Column(db.Date)
    archive_date = db.Column(db.Date)

    def __init__(self, nl_title='', nl_content='', en_title='', en_content='',
                 user_id=None, archive_date=None, publish_date=date.today()):

        self.title = None
        self.content = None
        self.nl_title = nl_title
        self.nl_content = nl_content
        self.en_title = en_title
        self.en_content = en_content

        self.user_id = user_id
        self.archive_date = archive_date
        self.publish_date = publish_date

    def get_short_content(self, characters):
        """Get a shortened version of the total post."""
        if len(self.content) > characters:
            short_content = self.content[:characters].strip()

            # Remove the last word
            words = short_content.split(' ')[:-1]

            return ' '.join(words) + '<br/><small><a href="' +\
                url_for('news.view', news_id=self.id) +\
                '">(' + _('Read more') + '...)</a></small>'

        return self.content


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
    locale = get_locale()
    nl_available = news.nl_title and news.nl_content
    en_available = news.en_title and news.en_content
    if locale == 'nl' and nl_available:
        news.title = news.nl_title
        news.content = news.nl_content
    elif locale == 'en' and en_available:
        news.title = news.en_title
        news.content = news.en_content
    elif nl_available:
        news.title = news.nl_title + " (" + _('Dutch') + ")"
        news.content = news.nl_content
    elif en_available:
        news.title = news.en_title + " (" + _('English') + ")"
        news.content = news.en_content
    else:
        news.title = 'N/A'
        news.content = 'N/A'
