import datetime
from functools import wraps

from flask import Blueprint, request, render_template, redirect, url_for, \
    flash, Response, abort
from flask_babel import _

import app.utils.committee as CommitteeAPI
from app import app, db
from app.decorators import require_role
from app.forms.newsletter import NewsletterForm
from app.models.news import News
from app.models.newsletter import Newsletter
from app.roles import Roles

blueprint = Blueprint('newsletter', __name__, url_prefix='/newsletter')


@blueprint.route('/', methods=['GET'])
@require_role(Roles.NEWS_WRITE)
def all():
    newsletters = Newsletter.query.all()
    auth_token = app.config['COPERNICA_NEWSLETTER_TOKEN']
    return render_template('newsletter/view.htm', newsletters=newsletters,
                           token=auth_token)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:newsletter_id>/', methods=['GET', 'POST'])
@require_role(Roles.NEWS_WRITE)
def edit(newsletter_id=None):
    if newsletter_id:
        newsletter = Newsletter.query.get_or_404(newsletter_id)
    else:
        newsletter = Newsletter()

    form = NewsletterForm(request.form, obj=newsletter)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(newsletter)
        db.session.add(newsletter)
        db.session.commit()

        flash(_('Newsletter saved'), 'success')
        return redirect(url_for('.all'))

    start_date = datetime.date.today().replace(day=1)
    prev_month = (start_date - datetime.timedelta(days=1)).replace(day=1)

    if not newsletter_id:
        selected_news_items = News.query.filter(
            News.created > prev_month, db.or_(
                News.archive_date >= datetime.date.today(),
                News.archive_date == None))\
            .order_by(News.created).all()  # noqa
    else:
        selected_news_items = []

    return render_template('newsletter/edit.htm', newsletter=newsletter,
                           form=form, selected_news_items=selected_news_items)


@blueprint.route('/delete/<int:newsletter_id>/', methods=['GET', 'POST'])
@require_role(Roles.NEWS_WRITE)
def delete(newsletter_id):
    if request.method == 'GET':
        return render_template('newsletter/confirm.htm')

    newsletter = Newsletter.query.get_or_404(newsletter_id)
    db.session.delete(newsletter)
    db.session.commit()

    return redirect(url_for('.all'))


def correct_token_provided(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args.get('auth_token')
        if token and app.config['COPERNICA_NEWSLETTER_TOKEN'] == token:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return wrapper


def get_newsletter(newsletter_id=None):
    if newsletter_id:
        return Newsletter.query.get_or_404(newsletter_id)
    else:
        return Newsletter.query.order_by(Newsletter.id.desc()).first()


@blueprint.route('/latest/committees/', methods=['GET'])
@correct_token_provided
def committees_xml():
    committees = CommitteeAPI.get_alphabetical()
    new_members = [c for c in committees if c.open_new_members]

    return Response(
        render_template('newsletter/committees.xml', items=new_members),
        mimetype='text/xml')


@blueprint.route('/<int:newsletter_id>/activities/', methods=['GET'])
@blueprint.route('/latest/activities/', methods=['GET'])
@correct_token_provided
def activities_xml(newsletter_id=None):
    newsletter = get_newsletter(newsletter_id)
    items = newsletter.activities if newsletter else []
    return Response(
        render_template('newsletter/activities.xml', items=items),
        mimetype='text/xml')


@blueprint.route('/<int:newsletter_id>/news/', methods=['GET'])
@blueprint.route('/latest/news/', methods=['GET'])
@correct_token_provided
def news_xml(newsletter_id=None):
    newsletter = get_newsletter(newsletter_id)
    items = newsletter.news_items if newsletter else []
    return Response(
        render_template('newsletter/news.xml', items=items),
        mimetype='text/xml')
