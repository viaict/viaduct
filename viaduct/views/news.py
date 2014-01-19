from flask import abort, render_template
from flask import Blueprint
from viaduct.models.news import News
from viaduct.api.group import GroupPermissionAPI
from datetime import datetime

#blueprint = Blueprint('news', __name__, url_prefix='/news')
blueprint = Blueprint('news', __name__)


@blueprint.route('/news/', methods=['GET'])
@blueprint.route('/news/page/<int:page_nr>/', methods=['GET'])
@blueprint.route('/news/<string:archive>/', methods=['GET'])
@blueprint.route('/news/<string:archive>/page/<int:page_nr>/', methods=['GET'])
def list(page_nr=1, archive=''):
    if not GroupPermissionAPI.can_read('news'):
        return abort(403)

    if archive == 'archive':
        items = News.query.filter(News.end_time < datetime.today())\
            .order_by(News.updated_time.desc())
    else:
        items = News.query.filter(News.end_time >= datetime.today())\
            .order_by(News.updated_time.asc())

    return render_template('news/list.htm', items=items.paginate(page_nr, 10,
                                                                 False),
                           archive=archive)
