import datetime

from app import db
from app.models.base_model import BaseEntity

newsletter_activities = db.Table(
    'newsletter_activities',
    db.Column('newsletter_id', db.Integer, db.ForeignKey('newsletter.id')),
    db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'))
)

newsletter_news = db.Table(
    'newsletter_news',
    db.Column('newsletter_id', db.Integer, db.ForeignKey('newsletter.id')),
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'))
)


class Newsletter(db.Model, BaseEntity):
    __tablename__ = 'newsletter'
    activities = db.relationship('Activity', secondary=newsletter_activities)
    news_items = db.relationship('News', secondary=newsletter_news,
                                 order_by="News.publish_date")

    def __init__(self, start_day=None):
        if start_day is None:
            start_day = datetime.date.today()

        weekday = start_day.weekday()
        self.start_day = start_day - datetime.timedelta(days=weekday)
