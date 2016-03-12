from flask import Blueprint, render_template, abort, request, flash, \
    redirect, url_for
from flask.ext.babel import _

from app import db
from app.helpers import flash_form_errors
from app.helpers.resource import get_all_routes
from app.models.navigation import NavigationEntry
from app.forms import NavigationEntryForm
from app.api.navigation import NavigationAPI
from app.api.module import ModuleAPI
from app.api.page import PageAPI
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

    entries = NavigationAPI.get_entries()

    return render_template('navigation/view.htm', nav_entries=entries)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/create/<int:parent_id>/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:entry_id>/', methods=['GET', 'POST'])
def edit(entry_id=None, parent_id=None):
    if not ModuleAPI.can_read('navigation'):
        return abort(403)

    if entry_id:
        entry = db.session.query(NavigationEntry)\
            .filter_by(id=entry_id).first()
        if not entry:
            return abort(404)
    else:
        entry = None
    form = NavigationEntryForm(request.form, entry)

    if parent_id:
        parent = NavigationEntry.query.filter_by(id=parent_id).first()
        if not parent:
            flash(_('Cannot find parent navigation entry.'), 'danger')
            return redirect(url_for('navigation.view'))

    if form.validate_on_submit():
        url = form.url.data
        if not re.compile('^/').match(url):
            url = '/' + url

        if entry:
            entry.nl_title = form.nl_title.data
            entry.en_title = form.en_title.data
            entry.url = url
            entry.external = form.external.data
            entry.activity_list = form.activity_list.data
        else:
            # If there is no parent position the new entry at the end of the
            # top level entry.
            if not parent_id:
                parent = None

                last_entry = db.session.query(NavigationEntry)\
                    .filter_by(parent_id=None)\
                    .order_by(NavigationEntry.position.desc()).first()

                position = last_entry.position + 1
            else:
                last_entry = db.session.query(NavigationEntry)\
                    .filter_by(parent_id=parent_id)\
                    .order_by(NavigationEntry.position.desc()).first()
                if last_entry:
                    position = last_entry.position + 1
                else:
                    position = 0

            entry = NavigationEntry(parent,
                                    form.nl_title.data,
                                    form.en_title.data,
                                    url,
                                    form.external.data,
                                    form.activity_list.data,
                                    position)

        db.session.add(entry)
        db.session.commit()
        flash(_('The navigation entry has been saved.'), 'success')

        if not form.external.data:

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

    parents = db.session.query(NavigationEntry).filter_by(parent_id=None)

    if entry:
        parents = parents.filter(NavigationEntry.id != entry.id)

    parents = parents.all()

    return render_template('navigation/edit.htm', entry=entry, form=form,
                           parents=parents)


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
