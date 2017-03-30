from flask import Blueprint, render_template, abort, request, flash, \
    redirect, url_for
from flask_babel import _

from app import db
from app.utils.forms import flash_form_errors
from app.utils.resource import get_all_routes
from app.forms import NavigationEntryForm
from app.utils.navigation import NavigationAPI
from app.utils.module import ModuleAPI
from app.utils.page import PageAPI
from app.models.navigation import NavigationEntry
from app.models.page import Page

import json
import re

blueprint = Blueprint('navigation', __name__, url_prefix='/navigation')


@blueprint.route('/edit/')
def edit_back():
    if not ModuleAPI.can_read('navigation'):
        return abort(403)

    return redirect(url_for('navigation.view'))


@blueprint.route('/')
def view():
    if not ModuleAPI.can_read('navigation'):
        return abort(403)

    entries = NavigationAPI.get_root_entries()
    return render_template('navigation/view.htm', nav_entries=entries)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/create/<int:parent_id>/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:entry_id>/', methods=['GET', 'POST'])
def edit(entry_id=None, parent_id=None):
    if not ModuleAPI.can_read('navigation'):
        return abort(403)

    entry = NavigationEntry.query.get_or_404(entry_id) if entry_id else None
    form = NavigationEntryForm(request.form, entry)
    form.page_id.choices = [(-1, '-- {} --'.format(_('Custom URL')))] + \
        db.session.query(Page.id, Page.path).all()

    parent = NavigationEntry.query.get(parent_id) if parent_id else None
    if parent_id and not parent:
        flash(_('Cannot find parent navigation entry.'), 'danger')
        return redirect(url_for('navigation.view'))

    if form.validate_on_submit():
        url = None
        if form.page_id.data == -1:
            url = form.url.data
            if not re.compile('^/').match(url):
                url = '/' + url

        page_id = None if form.page_id.data == -1 else form.page_id.data

        if entry:
            entry.nl_title = form.nl_title.data
            entry.en_title = form.en_title.data
            entry.url = url
            entry.page_id = page_id
            entry.external = form.external.data
            entry.activity_list = form.activity_list.data
        else:
            last_entry = NavigationEntry.query.filter_by(parent_id=None) \
                .order_by(NavigationEntry.position.desc()).first()

            # If there is no parent position the new entry at the end of the
            # top level entry.
            position = (last_entry.position + 1) if last_entry else 0

            entry = NavigationEntry(parent, form.nl_title.data,
                                    form.en_title.data, url, page_id,
                                    form.external.data,
                                    form.activity_list.data, position)

        db.session.add(entry)
        db.session.commit()
        flash(_('The navigation entry has been saved.'), 'success')

        if not page_id and not form.external.data:
            # Check if the page exists, if not redirect to create it
            path = form.url.data.lstrip('/')
            page = Page.get_by_path(path)
            if url.rstrip('/') in get_all_routes():
                return redirect(url_for('navigation.view'))
            if not page and form.url.data != '/':
                flash(_('The link refers to a page that does not exist, please'
                        'create the page!'), 'warning')
                return redirect(url_for('page.edit_page', path=path))

        return redirect(url_for('navigation.view'))

    else:
        flash_form_errors(form)

    parents = NavigationEntry.query.filter_by(parent_id=None)
    if entry:
        parents = parents.filter(NavigationEntry.id != entry.id)

    return render_template('navigation/edit.htm', entry=entry, form=form,
                           parents=parents.all())


@blueprint.route('/delete/<int:entry_id>/', methods=['GET'])
@blueprint.route('/delete/<int:entry_id>/<int:inc_page>', methods=['GET'])
def delete(entry_id, inc_page=0):
    if not ModuleAPI.can_write('navigation'):
        return abort(403)

    if inc_page and not ModuleAPI.can_write('page'):
        flash(_('You do not have rights to remove pages'))
        return abort(403)

    entry = db.session.query(NavigationEntry).filter_by(id=entry_id).first()
    if not entry:
        abort(404)

    if not entry.parent:
        if entry.children.count() > 0:
            flash('Deze item heeft nog subitems.', 'danger')
            return redirect(url_for('navigation.edit', entry_id=entry.id))

    if inc_page:
        if entry.external or entry.activity_list:
            flash('Deze item verwijst niet naar een pagina op deze website.',
                  'danger')
        else:
            path = entry.url.lstrip('/')
            if PageAPI.remove_page(path):
                flash('De pagina is verwijderd.', 'success')
            else:
                flash('De te verwijderen pagina kon niet worden gevonden.',
                      'danger')

    db.session.delete(entry)
    db.session.commit()

    flash('De navigatie-item is verwijderd.', 'success')

    return redirect(url_for('navigation.view'))


@blueprint.route('/navigation/reorder', methods=['POST'])
def reorder():
    if not ModuleAPI.can_write('navigation'):
        return abort(403)

    entries = json.loads(request.form['entries'])
    NavigationAPI.order(entries, None)

    return ""
