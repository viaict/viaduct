from flask import Blueprint, render_template, abort, request, flash, redirect,\
from flask.ext.login import current_user

from viaduct import db
from viaduct.helpers import flash_form_errors
from viaduct.models.navigation import NavigationEntry
from viaduct.forms import NavigationEntryForm

blueprint = Blueprint('navigation', __name__)

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
			abort(404)
	else:
		entry = None

    form = NavigationEntryForm(request.form, entry)

    if form.is_submitted():
        if form.validate_on_submit():
            if entry:
                entry.title = form.title.data
                entry.url = form.url.data
                entry.external = form.external.data

                db.session.add(entry)
                db.session.commit()

                flash('De item is opgeslagen.', 'success');
            else:
                entry = NavigationEntry(None, form.title.data, form.url.data,
                        form.external.data)

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

    return render_template('navigation/edit.htm', entry=entry, form=form)

@blueprint.route('/navigation/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
<<<<<<< HEAD
    entry = db.session.query(NavigationEntry).filter_by(id=entry_id).first()
    if not entry:
        abort(404)
=======
	if not current_user or current_user.email != 'administrator@svia.nl':
		return abort(403)

	entry = db.session.query(NavigationEntry).filter_by(id=entry_id).first()
	if not entry:
		abort(404)
>>>>>>> Permission check. Temporary.

    if not entry.parent:
        if entry.children:
            flash('Deze item heeft nog subitems.', 'error')
            return redirect(url_for('navigation.edit', entry_id=entry.id))

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for('navigation.view'))
