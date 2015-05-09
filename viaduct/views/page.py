# -*- coding: utf-8 -*-

import difflib

from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import current_user
from flask import abort

from viaduct import db
from viaduct.forms import PageForm, HistoryPageForm
from viaduct.models import Group, Page, PageRevision, PagePermission, \
    CustomForm
from viaduct.api.module import ModuleAPI
from viaduct.api.page import PageAPI

blueprint = Blueprint('page', __name__)


@blueprint.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
    path = Page.strip_path(path)
    page = Page.get_by_path(path)

    if not page:
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

        diff = difflib.HtmlDiff()\
            .make_table(previous_revision.get_comparable().splitlines(),
                        current_revision.get_comparable().splitlines())

        return render_template('page/compare_page_history.htm', diff=diff)

    return render_template('page/get_page_history.htm', form=form,
                           revisions=zip(revisions, form.previous,
                                         form.current))


@blueprint.route('/edit/<path:path>', methods=['GET', 'POST'])
def edit_page(path=''):
    if not ModuleAPI.can_write('page'):
        return abort(403)

    page = Page.get_by_path(path)

    data = request.form
    if page:
        revision = page.get_latest_revision()

        # Add the `needs_payed` option to the revision, so it will be inside
        # the form.
        revision.needs_payed = revision.page.needs_payed

        form = PageForm(data, revision)
    else:
        form = PageForm()

    form.custom_form_id.choices = \
        [(c.id, c.name) for c in CustomForm.query.order_by('name')]
    form.custom_form_id.choices.insert(0, (0, 'Geen formulier'))

    groups = Group.query.all()

    # on page submit (edit or create)
    if form.validate_on_submit():
        # if there was no page we want to create an entire new page (and not
        # just a revision)
        if not page:
            page = Page(path)

        page.needs_payed = 'needs_payed' in data

        db.session.add(page)
        db.session.commit()

        custom_form_id = int(data['custom_form_id'])
        if not custom_form_id:
            custom_form_id = None

        new_revision = PageRevision(page, data['title'].strip(),
                                    data['comment'].strip(), current_user,
                                    data['content'].strip(),
                                    'filter_html' in data, custom_form_id)

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

        flash('The page has been saved.', 'success')

        # redirect newly created page
        return redirect(url_for('page.get_page', path=path))
    else:
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
        flash('The page has been removed.', 'success')
    else:
        flash('The page you are trying to remove does not exist.', 'danger')

    return redirect(url_for('home.home'))
