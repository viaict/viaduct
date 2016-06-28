# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request,\
    url_for, abort
from flask_login import current_user
from flask_babel import _  # gettext

from app import db
from app.forms import PageForm, HistoryPageForm
from app.utils.forms import flash_form_errors
from app.utils.htmldiff import htmldiff
from app.models import Group, Page, PageRevision, PagePermission, Redirect
from app.utils.module import ModuleAPI
from app.utils.page import PageAPI

blueprint = Blueprint('page', __name__)


@blueprint.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
    path = Page.strip_path(path)
    page = Page.get_by_path(path)

    if not page:
        # Try if this might be a redirect.
        redirection = Redirect.query.filter(Redirect.fro == path).first()
        if redirection:
            return redirect(redirection.to)

        return abort(404)

    if not PageAPI.can_read(page):
        return abort(403)

    revision = page.get_latest_revision()

    if not revision:
        return abort(500)

    return render_template('%s/view_single.htm' % (page.type), page=page,
                           revision=revision, title=revision.title,
                           context=revision.__class__.context)


@blueprint.route('/history/<path:path>', methods=['GET', 'POST'])
def get_page_history(path=''):
    form = HistoryPageForm(request.form)

    page = Page.get_by_path(path)

    if not page:
        return abort(404)

    if not PageAPI.can_write(page):
        return abort(403)

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
def edit_page(path=''):
    if not ModuleAPI.can_write('page'):
        return abort(403)

    page = Page.get_by_path(path)
    form = request.form

    if page:
        revision = page.get_latest_revision()

        # Add the `needs_payed` option to the revision, so it will be inside
        # the form.
        revision.needs_payed = revision.page.needs_payed

        form = PageForm(form, revision)
    else:
        form = PageForm()

    groups = Group.query.all()

    # on page submit (edit or create)
    if form.validate_on_submit():
        # if there was no page we want to create an entire new page (and not
        # just a revision)
        if not page:
            page = Page(path)

        page.needs_payed = form['needs_payed'].data

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

        # Enter permission in db
        for form_entry, group in zip(form.permissions, groups):
            permission_entry = PagePermission.query\
                .filter(PagePermission.group_id == group.id,
                        PagePermission.page_id == page.id).first()

            permission_level = form_entry.select.data

            if permission_entry:
                permission_entry.permission = permission_level
            else:
                permission_entry = PagePermission(group.id, page.id,
                                                  permission_level)

            db.session.add(permission_entry)
            db.session.commit()

        flash(_('The page has been saved'), 'success')

        # redirect newly created page
        return redirect(url_for('page.get_page', path=path))
    else:
        flash_form_errors(form)
        for group in groups:
            permission = None
            if page:
                permission = PagePermission.query\
                    .filter(PagePermission.group_id == group.id,
                            PagePermission.page_id == page.id)\
                    .first()

            if permission:
                form.permissions\
                    .append_entry({'select': permission.permission})
            else:
                form.permissions.append_entry({})

    return render_template('page/edit_page.htm', page=page, form=form,
                           path=path, groups=zip(groups, form.permissions))


@blueprint.route('/remove/<path:path>/', methods=['POST'])
def delete(path):
    if not ModuleAPI.can_write('page'):
        return abort(403)

    if PageAPI.remove_page(path):
        flash(_('The page has been deletd'), 'success')
    else:
        flash(_('The page you tried to delete does not exist'), 'danger')

    return redirect(url_for('home.home'))
