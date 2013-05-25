from flask import Blueprint, render_template, abort, request, flash, redirect,\
from flask.ext.login import current_user

from viaduct import db
from viaduct.helpers import flash_form_errors
from viaduct.models.navigation import NavigationEntry
from viaduct.forms import NavigationEntryForm
from viaduct.api.navigation import NavigationAPI

import json

blueprint = Blueprint('navigation', __name__)

@blueprint.route('/navigation/edit')
def edit_back():
	return redirect(url_for('navigation.view'))

@blueprint.route('/navigation/')
def view():
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	entries = NavigationEntry.get_entries()

	return render_template('navigation/view.htm', entries=entries)

@blueprint.route('/navigation/create', methods=['GET', 'POST'])
@blueprint.route('/navigation/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id=None):
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	if entry_id:
		entry = db.session.query(NavigationEntry).filter_by(id=entry_id).first()
		if not entry:
			return abort(404)
	else:
		entry = None

    form = NavigationEntryForm(request.form, entry)

	if form.is_submitted():
		if form.validate_on_submit():
			if entry:
				entry.title = form.title.data
				entry.url = form.url.data
				entry.external = form.external.data
				entry.activity_list = form.activity_list.data

                db.session.add(entry)
                db.session.commit()

				flash('De item is opgeslagen.', 'success');
			else:
				last_entry = db.session.query(NavigationEntry)\
						.filter_by(parent_id=None)\
						.order_by(NavigationEntry.position.desc()).first()

				entry = NavigationEntry(None, form.title.data, form.url.data,
						form.external.data, form.activity_list.data,
						last_entry.position + 1)

                db.session.add(entry)
                db.session.commit()

                flash('De item is aangemaakt.', 'success');

                return redirect(url_for('navigation.edit', entry_id=entry.id))
        else:
            known_error = False;
            if not form.title.data:
                flash('Geen titel opgegeven.', 'error')
                known_error = True

            if not form.url.data:
                flash('Geen url opgegeven.', 'error')
                known_error = True

            if not known_error:
                flash_form_errors(form)

	parents = db.session.query(NavigationEntry).filter_by(parent_id=None)

	if entry:
		parents = parents.filter(NavigationEntry.id != entry.id)

	parents = parents.all()

	return render_template('navigation/edit.htm', entry=entry, form=form,
			parents=parents)

@blueprint.route('/navigation/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	entry = db.session.query(NavigationEntry).filter_by(id=entry_id).first()
	if not entry:
		abort(404)

    if not entry.parent:
        if entry.children:
            flash('Deze item heeft nog subitems.', 'error')
            return redirect(url_for('navigation.edit', entry_id=entry.id))

    db.session.delete(entry)
    db.session.commit()

	return redirect(url_for('navigation.view'))

@blueprint.route('/navigation/reorder', methods=['POST'])
def reorder():
	entries = json.loads(request.form['entries'])
	NavigationAPI.order(entries, None)

	return ""
