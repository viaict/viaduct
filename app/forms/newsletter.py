import datetime
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from app import db
from app.forms.fields import OrderedQuerySelectMultipleField
from app.models.activity import Activity
from app.models.news import News


def news_factory():
    now = datetime.date.today()

    return News.query.filter(db.or_(News.archive_date >= now,
                                    News.archive_date == None))\
                     .order_by(News.created).all()  # noqa


def activities_factory():
    start_date = datetime.date.today()
    return Activity.query.filter(Activity.end_time > start_date)\
                         .order_by(Activity.start_time).all()


class NewsletterForm(FlaskForm):
    activities = OrderedQuerySelectMultipleField(
        _('Activities'), query_factory=activities_factory)
    news_items = OrderedQuerySelectMultipleField(
        _('News items'), query_factory=news_factory)
