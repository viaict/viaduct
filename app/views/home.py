from datetime import date, datetime
from flask import Blueprint, render_template, abort
from flask_babel import _
from sqlalchemy import desc

from app import db
from app.models import News
from app.models.page import Page, PageRevision
from app.models.activity import Activity

blueprint = Blueprint('home', __name__)


@blueprint.route('/', methods=['GET'])
def home():
    data = ['activities',
            'contact']

    pages = []
    revisions = []

    for path in data:
        if path == 'activities':
            revision = PageRevision(None, None, None, None, None, None, None)

            activities = Activity.query \
                .filter(Activity.end_time > datetime.now()) \
                .order_by(Activity.start_time.asc())
            revision.activity = \
                render_template('activity/view_simple.htm',
                                activities=activities.paginate(1, 4, False))

            revisions.append(revision)

            continue

        page = Page.get_by_path(Page.strip_path(path))
        pages.append(page)

        if not page:
            revision = PageRevision(None, None, None, None, None, None, None)
            revision.title = _('Not found!')
            revision.content = _('Page not found')

            revisions.append(revision)

            continue

        revision = page.get_latest_revision()
        revision.test = path
        if not revision:
            return abort(500)

        revisions.append(revision)

    news = News.query.filter(
        db.and_(
            db.or_(
                News.archive_date >= date.today(), News.archive_date == None),
            News.publish_date <= date.today()))\
        .order_by(desc(News.publish_date)).limit(8).all()  # noqa

    return render_template('home/home.htm', revisions=revisions,
                           title='Homepage', news=news)
