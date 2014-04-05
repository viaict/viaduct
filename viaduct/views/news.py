from datetime import datetime, date

from flask import Blueprint, abort, render_template, request, flash, redirect,\
    url_for
from flask.ext.login import current_user

from viaduct import db
from viaduct.api import GroupPermissionAPI
from viaduct.forms import NewsForm
from viaduct.models import NewsRevision, Page

blueprint = Blueprint('news', __name__)


@blueprint.route('/news/', methods=['GET'])
@blueprint.route('/news/page/<int:page_nr>/', methods=['GET'])
def list(page_nr=1):
    if not GroupPermissionAPI.can_read('news'):
        return abort(403)

    archive = int(request.args.get('archive', 0))

    itemsub = db.session.query(db.func.max(NewsRevision.id)
                               .label('max_id'))\
        .group_by(NewsRevision.instance_id).subquery()

    items = NewsRevision.query\
        .join(itemsub, NewsRevision.id == itemsub.c.max_id)

    if archive:
        items = items.filter(db.or_(NewsRevision.end_time < date.today(),
                                    NewsRevision.end_time != None))
    else:
        items = items.filter(db.or_(NewsRevision.end_time >= date.today(),
                                    NewsRevision.end_time == None))

    items = items.paginate(page_nr, 20)

    return render_template('news/list.htm', items=items, archive=archive)


@blueprint.route('/create/news/', methods=['GET', 'POST'])
@blueprint.route('/edit/news/<int:instance_id>/', methods=['GET', 'POST'])
def edit(instance_id=None):
    if not GroupPermissionAPI.can_write('news'):
        return abort(403)

    data = request.form
    if instance_id:
        revision = NewsRevision.get_latest(instance_id)

        if not revision:
            return abort(404)

        page = revision.page

        revision.needs_payed = page.needs_payed

        form = NewsForm(data, revision)
    else:
        instance_id = NewsRevision.get_new_id()
        form = NewsForm()
        page = None

    if form.validate_on_submit():
        if not page:
            page = Page('news/%d/' % (instance_id), 'news')

        page.needs_payed = 'needs_payed' in data

        db.session.add(page)
        db.session.commit()

        end_time = datetime.strptime(data['end_time'], '%Y-%m-%d').date()
        end_time = None
        new_revision = NewsRevision(page, data['title'].strip(),
                                    data['comment'].strip(), instance_id,
                                    data['content'].strip(), current_user.id,
                                    end_time)

        db.session.add(new_revision)
        db.session.commit()

        flash('Nieuwsitem opgeslagen.', 'success')

        return redirect(url_for('page.get_page', path=page.path))

    return render_template('news/edit.htm', page=page, form=form)
