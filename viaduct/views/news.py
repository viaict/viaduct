from flask import abort, render_template, flash, redirect, url_for, request
from flask import Blueprint
from flask.ext.login import current_user
from viaduct import db
from viaduct.models.news import News
from viaduct.forms.news import NewsForm
from viaduct.api.group import GroupPermissionAPI
from viaduct.helpers import flash_form_errors
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
@blueprint.route('/news/item/<int:item_id>/edit/', methods=['GET'])
def edit(item_id=None):
    if not GroupPermissionAPI.can_write('news'):
        return abort(403)

    if item_id:
        item = News.query.get(item_id)

        if not item:
            flash('Nieuwsartikel niet gevonden', 'error')
            return abort(404)
    else:
        item = News()

    form = NewsForm(request.form, item)

    return render_template('news/edit.htm', item=item, form=form)


@blueprint.route('/news/item/new/', methods=['POST'])
@blueprint.route('/news/item/<int:item_id>/edit/', methods=['POST'])
def update(item_id=None):
    if not GroupPermissionAPI.can_write('news'):
        return abort(403)

    if item_id:
        item = News.query.get(item_id)

        if not item:
            flash('Nieuwsartikel niet gevonden', 'error')
            return abort(404)
    else:
        item = News()

    form = NewsForm(request.form, item)

    if form.validate_on_submit():
        item.title = form.title.data
        item.content = form.content.data
        item.end_time = form.end_time.data

        if item_id:
            item.update_time = datetime.now()
        else:
            item.author_id = current_user.id
            item.post_time = datetime.now()
            item.update_time = item.post_time

        db.session.add(item)
        db.session.commit()

        flash('Nieuwsartikel opgeslagen', 'success')

        return redirect(url_for('news.single', item_id=item.id))
    else:
        flash_form_errors(form)
        return render_template('news/edit.htm', item=item, form=form)
