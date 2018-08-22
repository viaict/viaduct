# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, \
    url_for, abort, make_response, current_app
from flask_babel import _  # gettext
from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.urls import iri_to_uri
from wtforms.fields import StringField

from app import db
from app.decorators import require_role
from app.forms import init_form
from app.forms.page import PageForm, HistoryPageForm
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult
from app.models.page import Page, PageRevision
from app.models.redirect import Redirect
from app.roles import Roles
from app.service import role_service, page_service
from app.utils.forms import flash_form_errors
from app.utils.htmldiff import htmldiff

blueprint = Blueprint('page', __name__)


@blueprint.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
    path = Page.strip_path(path)
    page = page_service.get_page_by_path(path)

    if not page:
        # Try if this might be a redirect.
        redirection = Redirect.query.filter(Redirect.fro == path).first()
        if redirection:

            # get GET parameters so they can be applied to the redirected
            # URL
            if request.args:
                redir_url = redirection.to + '?'
                for key in request.args:
                    redir_url += key + '=' + \
                        request.args[key] + '&'

                # this is necssary to prevent incorrect escaping
                return redirect(iri_to_uri(redir_url))

            return redirect(redirection.to)

        return abort(404)

    if not page_service.can_user_read_page(page, current_user):
        return abort(403)

    revision = page.get_latest_revision()

    if not revision:
        return abort(500)

    # Check if the current user has already entered data in this custom
    # form
    if getattr(revision, 'custom_form', False):
        if current_user.is_authenticated and current_user.has_paid:
            all_form_results = CustomFormResult.query \
                .filter(CustomFormResult.form_id == revision.custom_form.id)
            form_result = all_form_results \
                .filter(CustomFormResult.owner_id == current_user.id).first()

            if form_result:
                revision.custom_form_data = form_result.data.replace('"', "'")
    can_write = role_service.user_has_role(current_user, Roles.PAGE_WRITE)
    return render_template('%s/view_single.htm' % (page.type), page=page,
                           revision=revision, title=revision.title,
                           context=revision.__class__.context,
                           can_write=can_write)


@blueprint.route('/history/<path:path>', methods=['GET', 'POST'])
@require_role(Roles.PAGE_WRITE)
def get_page_history(path=''):
    form = HistoryPageForm(request.form)

    page = page_service.get_page_by_path(path)

    if not page:
        return abort(404)

    revisions = page.revision_cls.get_query()\
        .filter(page.revision_cls.page_id == page.id)\
        .all()

    form.previous.choices = [(revision.id, '') for revision in revisions]
    form.current.choices = [(revision.id, '') for revision in revisions]

    if form.validate_on_submit():
        previous = request.form['previous']
        current = request.form['current']

        previous_revision = page.revision_cls.get_query()\
            .filter(page.revision_cls.id == previous).first()
        current_revision = page.revision_cls.get_query()\
            .filter(page.revision_cls.id == current).first()

        prev = previous_revision.get_comparable()
        cur = current_revision.get_comparable()
        diff = htmldiff(prev, cur)

        return render_template('page/compare_page_history.htm', diff=diff)

    return render_template('page/get_page_history.htm', form=form,
                           revisions=zip(revisions, form.previous,
                                         form.current))


@blueprint.route('/edit/<path:path>', methods=['GET', 'POST'])
@require_role(Roles.PAGE_WRITE)
def edit_page(path=''):

    page = page_service.get_page_by_path(path)

    if page:
        revision = page.get_latest_revision()
        revision.read_groups = page_service.get_read_permission_groups_by_page(
            page)
        revision.needs_paid = page.needs_paid
        revision.custom_read_permission = page.custom_read_permission
    else:
        revision = None

    form = init_form(PageForm, obj=revision)

    if form.validate_on_submit():
        # if there was no page we want to create an entire new page (and not
        # just a revision)
        if not page:
            page = Page(path)

        page.needs_paid = form.needs_paid.data
        page.custom_read_permission = form.custom_read_permission.data

        db.session.add(page)
        db.session.commit()

        custom_form_id = int(form.custom_form_id.data)
        if custom_form_id == 0:
            custom_form_id = None

        new_revision = PageRevision(page,
                                    form.nl_title.data.strip(),
                                    form.en_title.data.strip(),
                                    form.comment.data.strip(),
                                    current_user,
                                    form.nl_content.data.strip(),
                                    form.en_content.data.strip(),
                                    'filter_html' in form,
                                    custom_form_id)

        db.session.add(new_revision)
        db.session.commit()

        if form.custom_read_permission.data:
            page_service.set_read_page_permissions(page, form.read_groups.data)
        else:
            page_service.delete_read_page_permission(page)

        flash(_('The page has been saved'), 'success')

        # redirect (newly) created page revision
        return redirect(url_for('page.get_page', path=path))

    return render_template('page/edit_page.htm', page=page, form=form)


@blueprint.route('/delete/<path:path>/', methods=['GET', 'POST'])
@require_role(Roles.PAGE_WRITE)
def delete(path):

    page = page_service.get_page_by_path(path)
    if not page:
        flash(_('The page you tried to delete does not exist.'), 'danger')
        return redirect(url_for('page.get_page', path=path))
    rev = page.get_latest_revision()

    class DeleteForm(FlaskForm):
        title = StringField(_('Page title'))

    form = DeleteForm(request.form)

    if form.validate_on_submit():
        if rev.title == form.title.data:
            db.session.delete(page)
            db.session.commit()
            flash(_('The page has been deleted'), 'success')
            return redirect(url_for('home.home'))
        else:
            flash(_('The given title does not match the page title.'),
                  'warning')
    else:
        flash_form_errors(form)

    return render_template('page/delete.htm', rev=rev, form=form)


# a route for generating sitemap.xml
@blueprint.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    ten_days_ago = datetime.now() - timedelta(days=10)
    pages = []
    only = ['activities', 'companies', 'vacancies', 'news']

    # static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            rule_split = rule.rule.split('/')
            if rule_split[1] in only and len(rule_split) <= 3:
                pages.append([rule.rule, ten_days_ago])

    activities = Activity.query.all()
    for activity in activities:
        pages.append(["/activities/%s" % activity.id, activity.modified])
    standalone_pages = Page.query.all()
    for page in standalone_pages:
        if not page.needs_paid:
            pages.append(["/%s" % page.path,
                          page.get_latest_revision().modified])
    sitemap_xml = render_template('page/sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response
