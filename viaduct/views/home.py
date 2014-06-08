from viaduct.models.page import Page, PageRevision
from viaduct.models.activity import Activity
from flask import Blueprint, render_template
from flask import abort
from viaduct import db
import datetime
#from viaduct.models.home import Homepage

blueprint = Blueprint('home', __name__)


@blueprint.route('/', methods=['GET'])
def home():
    data = ['laatste_bestuursblog',
            'activities',
            'twitter',
            'contact']

    pages = []
    revisions = []

    for path in data:
        page = Page.get_by_path(Page.strip_path(path))
        pages.append(page)

        if not page:
            return abort(404)

        revision = page.get_latest_revision()
        if not revision:
            return abort(500)

        if path == 'activities':
            activities = Activity.query \
                .filter(Activity.end_time > datetime.datetime.now()) \
                .order_by(Activity.start_time.asc())
            revision.activity = render_template('activity/view_simple.htm',
                                    activities=activities
                                    .paginate(1, 12, False))
            print(revision.activity)
        revisions.append(revision)

    for page in pages:
        print(page)

    for revision in revisions:
        print(revision.title)

    return render_template('home/home.htm', data=revisions)
