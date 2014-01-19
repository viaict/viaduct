from flask import abort, render_template, flash, redirect, url_for
from flask import Blueprint
from viaduct import db
from viaduct.models.news import News
from viaduct.api.group import GroupPermissionAPI
from datetime import datetime

#blueprint = Blueprint('news', __name__, url_prefix='/news')
blueprint = Blueprint('news', __name__)


@blueprint.route('/news/', methods=['GET'])
@blueprint.route('/news/<int:page_nr>/', methods=['GET'])
@blueprint.route('/news/<string:archive>/', methods=['GET'])
@blueprint.route('/news/<string:archive>/<int:page_nr>/', methods=['GET'])
def list(page_nr=1, archive=''):
    if not GroupPermissionAPI.can_read('news'):
        return abort(403)

    if archive == 'archive':
        items = News.query.filter(News.end_time < datetime.today())
    else:
        items = News.query.filter(News.end_time >= datetime.today())

    items = items.order_by(News.update_time.desc())

    return render_template('news/list.htm', items=items.paginate(page_nr, 10,
                                                                 False),
                           archive=archive)


@blueprint.route('/news/item/<int:item_id>/', methods=['GET'])
def single(item_id):
    if not GroupPermissionAPI.can_read('news'):
        return abort(403)

    item = News.query.get(item_id)

    if not item:
        return abort(404)

    return render_template('news/single.htm', item=item)


@blueprint.route('/news/item/<int:item_id>/delete/', methods=['POST'])
def delete(item_id):
    if not GroupPermissionAPI.can_write('news'):
        return abort(403)

    item = News.query.get(item_id)

    if not item:
        flash('Het nieuwsartikel kon niet gevonden worden', 'error')
        return abort(404)

    db.session.delete(item)
    db.session.commit()

    flash('Het nieuwsartikel is verwijderd', 'success')

    return redirect(url_for('news.list'))


@blueprint.route('/news/item/new/', methods=['GET'])
@blueprint.route('/news/item/<int:item_id/edit/', methods=['GET'])
def edit(item_id=None):
    pass
