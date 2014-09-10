from viaduct.models.page import Page, PageRevision
from viaduct.models.activity import Activity
from flask import Blueprint, render_template
from flask import abort
import datetime
#from viaduct.models.home import Homepage

blueprint = Blueprint('home', __name__)


@blueprint.route('/', methods=['GET'])
def home():
    data = ['laatste_bestuursblog',
            'activities',
            'contact']

    pages = []
    revisions = []

    for path in data:
        if path == 'activities':
            revision = PageRevision(None, None, None, None, None)

            activities = Activity.query \
                .filter(Activity.end_time > datetime.datetime.now()) \
                .order_by(Activity.start_time.asc())
            revision.activity = \
                render_template('activity/view_simple.htm',
                                activities=activities .paginate(1, 12, False))

            revisions.append(revision)

            continue

        page = Page.get_by_path(Page.strip_path(path))
        pages.append(page)

        if not page:
            revision = PageRevision(None, None, None, None, None)
            revision.title = 'Not found!'
            revision.content = 'Page not found'

            revisions.append(revision)

            continue

        revision = page.get_latest_revision()
        revision.test = path
        if not revision:
            return abort(500)

        revisions.append(revision)

    return render_template('home/home.htm', data=revisions)
