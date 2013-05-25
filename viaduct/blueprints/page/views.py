from flask import Blueprint
from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from api import PageAPI
from models import Page, PageRevision, PagePermission
from forms import ChangePathForm, EditPageForm

blueprint = Blueprint('page', __name__)

@application.errorhandler(403)
@application.errorhandler(404)
def get_error_page(error):
	return render_template('page/view_page.htm')

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/page/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
	return render_template('page/view_page.htm', page=True, path=path)


@blueprint.route('/delete/')
@blueprint.route('/delete/<path:page_path>')
def delete_page(page_path='', revision=''):
	page = Page.query.filter(Page.path==page_path).first()
	revisions = PageRevision.query.filter(PageRevision.page_id==page.id).all()
	for revision in revisions:
		db.session.delete(revision)
	db.session.delete(page)
	db.session.commit()
	return redirect('/')

@blueprint.route('/edit/', methods=['GET', 'POST'])
@blueprint.route('/edit/<path:path>', methods=['GET', 'POST'])
def edit_page(path=''):
	rights = PagePermission.get_user_rights(current_user, path)

	if not rights['safe_edit'] or not rights['unsafe_edit']:
		abort(403)

	form = EditPageForm()

	form.content_type.choices = []

	if rights['unsafe_edit']:
		form.content_type.choices.append((1, 'HTML'))
		form.content_type.default = 1

	if rights['safe_edit']:
		form.content_type.choices.append((2, 'Markdown'))
		form.content_type.default = 2

	page = Page.query.filter(Page.path==path).first()
	revision = None

	if page:
		revision = page.revisions.order_by(PageRevision.timestamp.desc()).first()

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

	return render_template('page/edit_page.htm', form=form,
		revision=revision, page=path)

