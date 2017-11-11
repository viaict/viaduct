from datetime import date, datetime

from flask import Blueprint, abort, render_template, request, flash, \
    redirect, url_for
from flask_babel import _  # gettext
from flask_login import current_user
from sqlalchemy import desc
from werkzeug.contrib.atom import AtomFeed

from app import db
from app.decorators import require_role
from app.forms.news import NewsForm
from app.models.news import News
from app.roles import Roles

blueprint = Blueprint('news', __name__, url_prefix='/news')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/<int:page_nr>/', methods=['GET'])
def list(page_nr=1):
    items = News.query.filter(News.publish_date <= date.today(),
                              db.or_(News.archive_date >= date.today(),
                                     News.archive_date == None),  # noqa
                              db.or_(current_user.has_paid,
                                     db.not_(News.needs_paid))) \
        .order_by(desc(News.publish_date))

    return render_template('news/list.htm',
                           items=items.paginate(page_nr, 10, False),
                           archive=False)


@blueprint.route('/all/', methods=['GET'])
@blueprint.route('/all/<int:page_nr>/', methods=['GET'])
def all(page_nr=1):
    return render_template('news/list.htm',
                           items=News.query.paginate(page_nr, 10, False),
                           archive=False)


@blueprint.route('/archive/', methods=['GET'])
@blueprint.route('/archive/<int:page_nr>/', methods=['GET'])
def archive(page_nr=1):
    items = News.query.filter(db.and_(News.archive_date < date.today(),
                                      News.archive_date != None))  # noqa

    return render_template('news/list.htm',
                           items=items.paginate(page_nr, 10, False),
                           archive=True)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:news_id>/', methods=['GET', 'POST'])
@require_role(Roles.NEWS_WRITE)
def edit(news_id=None):
    if news_id:
        news_item = News.query.get_or_404(news_id)
    else:
        news_item = News()

    form = NewsForm(request.form, news_item)

    if form.validate_on_submit():

        # fill the news_item with the form entries.
        form.populate_obj(news_item)

        # Only set writer if post is brand new
        if not news_item.id:
            news_item.user_id = current_user.id

        db.session.add(news_item)
        db.session.commit()

        news_id = news_item.id
        flash(_('News item saved'), 'success')

        return redirect(url_for('news.view', news_id=news_id))

    return render_template('news/edit.htm', form=form, news_id=news_id)


@blueprint.route('/view/', methods=['GET'])
@blueprint.route('/view/<int:news_id>/', methods=['GET'])
def view(news_id=None):
    if not news_id:
        flash(_('This news item does not exist'), 'danger')
        return redirect(url_for('news.list'))

    news = News.query.get_or_404(news_id)
    if not news.can_read():
        return abort(403)

    return render_template('news/view_single.htm', news=news)


@blueprint.route('/delete/', methods=['GET'])
@blueprint.route('/delete/<int:news_id>/', methods=['GET'])
@require_role(Roles.NEWS_WRITE)
def delete(news_id=None):
    if not news_id:
        flash(_('This news item does not exist'), 'danger')
        return redirect(url_for('news.list'))

    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()

    flash(_('News item succesfully deleted'), 'success')

    return redirect(url_for('news.list'))


@blueprint.route('/rss/', methods=['GET'])
@blueprint.route('/rss/<string:locale>/')
def rss(locale='en'):
    name = 'via nieuws' if locale == 'nl' else 'via news'
    feed = AtomFeed(name, feed_url=request.url, url=request.url_root)
    items = News.query.filter(News.publish_date <= date.today(),
                              db.or_(News.archive_date >= date.today(),
                                     News.archive_date == None),  # noqa
                              db.or_(db.not_(News.needs_paid))) \
        .order_by(News.publish_date.desc()).limit(20)

    for item in items:
        published = datetime.combine(item.publish_date, datetime.min.time())
        title, content = item.get_localized_title_content(locale)
        feed.add(title, content, id=item.id, content_type='markdown',
                 published=published, updated=published,
                 url=url_for('news.view', news_id=item.id),
                 author=item.user.name)

    return feed.get_response()
