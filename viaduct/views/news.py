from flask import Blueprint, abort, render_template, request

from viaduct.api import GroupPermissionAPI
from viaduct.forms import NewsForm
from viaduct.models import NewsRevision
import viaduct.api.news as NewsAPI

blueprint = Blueprint('news', __name__)


@blueprint.route('/edit/news/<int:instance_id>/', methods=['GET', 'POST'])
def edit_news(instance_id):
    revision = NewsAPI.get_latest_revision(instance_id)

    if not revision:
        return abort(404)

    if not GroupPermissionAPI.can_write('news'):
        return abort(403)

    new_revision = NewsRevision(revision.page, revision.title, '',
                                revision.instance_id, revision.content,
                                revision.author_id, revision.end_time)

    new_revision.needs_payed = revision.page.needs_payed

    form = NewsForm(request.form, new_revision)

    return render_template('news/edit.htm', item=new_revision, form=form)
