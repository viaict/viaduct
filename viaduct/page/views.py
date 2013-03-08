from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from api import PageAPI
from models import Page, PageRevision, PagePermission
from forms import ChangePathForm

module = Blueprint('page', __name__)

@application.errorhandler(403)
@application.errorhandler(404)
def get_error_page(error):
	return render_template('page/view_page.htm')

@module.route('/', methods=['GET', 'POST'])
@module.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
	return render_template('page/view_page.htm', page=True, path=path)

@module.route('/delete/')
@module.route('/delete/<path:page_path>')
def delete_page(page_path='', revision=''):
	page = Page.query.filter(Page.path==page_path).first()
	revisions = PageRevision.query.filter(PageRevision.page_id==page.id).all()
	for revision in revisions:
		db.session.delete(revision)
	db.session.delete(page)
	db.session.commit()
	return redirect('/')

@module.route('/edit/', methods=['GET', 'POST'])
@module.route('/edit/<path:path>', methods=['GET', 'POST'])
def edit_page(path=''):
	rights = PagePermission.get_user_rights(current_user, path)

	if not rights['safe_edit'] or not rights['unsafe_edit']:
		abort(403)

	page = Page.get_page_by_path(path)
	revision = None

	if page:
		revision = page.get_newest_revision()

	if request.method == 'POST':
		title = request.form['title'].strip()
		content = request.form['content'].strip()
		try:
			priority = int(request.form['priority'].strip())
		except:
			priority = 0


		# A new page is being created
		if not page:
			page = Page(page_path)

			db.session.add(page)
			db.session.commit()

		revision = PageRevision(page, current_user, title, content, priority)

		db.session.add(revision)
		db.session.commit()

		flash('The page has been saved.', 'success')

		return redirect(url_for('page.get_page', page=True, path=page_path))

	return render_template('page/edit_page.htm', revision=revision, page=path)

