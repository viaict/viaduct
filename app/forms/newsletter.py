import datetime
from flask_babel import lazy_gettext as _
from flask_wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from app import db
from app.models.activity import Activity
from app.models.news import News


def news_factory():
    start_date = datetime.date.today().replace(day=1)
    prev_month = (start_date - datetime.timedelta(days=1)).replace(day=1)
    return News.query.filter(News.created > prev_month,
                             db.or_(News.archive_date >= datetime.date.today(),
                                    News.archive_date == None))\
                     .order_by(News.created).all()  # noqa


def activities_factory():
    start_date = datetime.date.today()
    return Activity.query.filter(Activity.start_time > start_date)\
                         .order_by(Activity.start_time).all()


class NewsletterForm(Form):
    activities = QuerySelectMultipleField(
        _('Activities'), query_factory=activities_factory)
    news_items = QuerySelectMultipleField(
        _('News items'), query_factory=news_factory)
