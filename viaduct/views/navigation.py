from flask import Blueprint, render_template, abort, request, flash, redirect,\
		url_for
from flask.ext.login import current_user

from viaduct import db, application
from viaduct.helpers import flash_form_errors
from viaduct.models.navigation import NavigationEntry
from viaduct.forms import NavigationEntryForm
from viaduct.api.navigation import NavigationAPI
from viaduct.api.group import GroupPermissionAPI
from viaduct.models.page import Page

import json
import re

blueprint = Blueprint('navigation', __name__, url_prefix='/navigation')

@blueprint.route('/edit/')
def edit_back():
	if not GroupPermissionAPI.can_read('navigation'):
		return abort(403)

	return redirect(url_for('navigation.view'))

@blueprint.route('/')
def view():
	if not GroupPermissionAPI.can_read('navigation'):
		return abort(403)

	entries = NavigationAPI.get_entries()

	return render_template('navigation/view.htm', nav_entries=entries)

@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/create/<int:parent_id>/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:entry_id>/', methods=['GET', 'POST'])
def edit(entry_id=None, parent_id=None):
	if not GroupPermissionAPI.can_read('navigation'):
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
			url = form.url.data
			pattern = re.compile('^/')
			if not pattern.match(url):
				url = '/' + url

			if entry:
				flash('De navigatie link is opgeslagen.', 'success');
				entry.title = form.title.data
				entry.url = url
				entry.external = form.external.data
				entry.activity_list = form.activity_list.data
			else:
				if not parent_id:
					parent = None

					last_entry = db.session.query(NavigationEntry)\
						.filter_by(parent_id=None)\
						.order_by(NavigationEntry.position.desc()).first()

					position = last_entry.position + 1
				else:
					parent = db.session.query(NavigationEntry) \
											.filter_by(id=parent_id).first()

					if not parent:
						flash('Deze navigatie parent bestaat niet.', 'error');
						return redirect(url_for('navigation.edit'))

					last_entry = db.session.query(NavigationEntry)\
						.filter_by(parent_id=parent.id)\
						.order_by(NavigationEntry.position.desc()).first()
					if last_entry:
						position = last_entry.position + 1
					else:
						position = 0

				entry = NavigationEntry(parent, form.title.data, url,
						form.external.data, form.activity_list.data, position)
				flash('De navigatie link is aangemaakt.', 'success');

			db.session.add(entry)
			db.session.commit()

			if not form.external.data:

				# Check if the page exists, if not redirect to create it
				page = Page.get_by_path(form.url.data)
				if not page and form.url.data != '/':
					flash('De link verwijst naar een pagina die niet bestaat, '
							'maak deze aub aan!', 'alert');
					return redirect(url_for('page.edit_page',
							path=form.url.data))

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

@blueprint.route('/delete/<int:entry_id>/', methods=['POST'])
def delete(entry_id):
	if not GroupPermissionAPI.can_write('navigation'):
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
	if not GroupPermissionAPI.can_write('navigation'):
		return abort(403)

	entries = json.loads(request.form['entries'])
	NavigationAPI.order(entries, None)

	return ""
