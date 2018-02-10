import datetime
from app import db
from app.models.base_model import BaseEntity

from sqlalchemy.ext.orderinglist import ordering_list


class NewsletterActivity(db.Model):
    __tablename__ = 'newsletter_activities'

    def __init__(self, activity=None):
        self.activity = activity

    newsletter_id = db.Column(db.Integer, db.ForeignKey('newsletter.id',
                                                        ondelete='cascade'),
                              nullable=False, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'),
                            nullable=False, primary_key=True)
    position = db.Column(db.Integer, nullable=False)

    activity = db.relationship('Activity')


class NewsletterNewsItem(db.Model):
    __tablename__ = 'newsletter_news'

    def __init__(self, news_item=None):
        self.news_item = news_item

    newsletter_id = db.Column(db.Integer, db.ForeignKey('newsletter.id',
                                                        ondelete='cascade'),
                              nullable=False, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'),
                        nullable=False, primary_key=True)
    position = db.Column(db.Integer, nullable=False)

    news_item = db.relationship('News')


class Newsletter(db.Model, BaseEntity):
    activities = db.relationship('NewsletterActivity',
                                 order_by='NewsletterActivity.position',
                                 collection_class=ordering_list('position'),
                                 cascade='all, delete-orphan')

    news_items = db.relationship('NewsletterNewsItem',
                                 order_by='NewsletterNewsItem.position',
                                 collection_class=ordering_list('position'),
                                 cascade='all, delete-orphan')

    def __init__(self, start_day=None):
        if start_day is None:
            start_day = datetime.date.today()

        weekday = start_day.weekday()
        self.start_day = start_day - datetime.timedelta(days=weekday)
