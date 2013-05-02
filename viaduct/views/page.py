from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from viaduct import db
from viaduct.helpers import flash_form_errors
from viaduct.forms import EditPageForm
from viaduct.blueprints.page.models import Page, PageRevision, PagePermission

blueprint = Blueprint('page2', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<path:path>', methods=['GET', 'POST'])
def get_page(path=''):
	revisions = []

	if path == '' or path == 'index':
		paths = ['index1', 'index2', 'index3', 'index4']
	else:
		paths = [path]

	for path in paths:
		page = Page.query.filter(Page.path==path).first()

		if not page:
			page = Page('')

		if page.revisions.count() > 0:
			revision = page.revisions.order_by(PageRevision.timestamp.desc()).first()
		else:
			revision = PageRevision(page, current_user, 'Oh no! It looks like
				you have found a dead Link!',
				'![alt text](../static/img/404.png "404")', True)

		revisions.append(revision)

	return render_template('page/get_page.htm', revisions=revisions)

@blueprint.route('/history/', methods=['GET', 'POST'])
@blueprint.route('/history/<path:path>', methods=['GET', 'POST'])
def get_page_history(path=''):
	page = Page.query.filter(Page.path==path).first()

	if not page:
		page = Page('')

	if page.revisions.count() > 0:
		revisions = page.revisions.order_by(PageRevision.timestamp.desc()).all()
	else:
		revisions = None

	return render_template('page/get_page_history.htm', revisions=revisions)

@blueprint.route('/edit/', methods=['GET', 'POST'])
@blueprint.route('/edit/<path:path>', methods=['GET', 'POST'])
def edit_page(path=''):
	page = Page.query.filter(Page.path==path).first()
	revision = None

	if page:
		revision = page.revisions.order_by(PageRevision.timestamp.desc()).first()
		revision.filter_html = not revision.filter_html

	form = EditPageForm(request.form, obj=revision)

	if form.validate_on_submit():
		title = request.form['title'].strip()
		content = request.form['content'].strip()
		comment = request.form['comment'].strip()

		if 'filter_html' in request.form:
			filter_html = False
		else:
			filter_html = True

		if not page:
			page = Page(path)

			db.session.add(page)
			db.session.commit()

		revision = PageRevision(page, current_user, title, content, comment,
			filter_html)

		db.session.add(revision)
		db.session.commit()

		flash('The page has been saved.', 'success')

		return redirect(url_for('page2.get_page', path=path))
	else:
		flash_form_errors(form)

	return render_template('page/edit_page.htm', form=form)

