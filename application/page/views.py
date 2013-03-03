from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from application import db
from application.helpers import flash_form_errors
from application.page.models import Page, PageRevision, PagePermission
from application.page.forms import ChangePathForm

page_module = Blueprint('page', __name__)

@page_module.route('/page/', methods=['GET', 'POST'])
@page_module.route('/page/<path:page_path>', methods=['GET', 'POST'])
def view_page(page_path=''):
	rights = PagePermission.get_user_rights(current_user, page_path)
	form = ChangePathForm()

	if not rights['view']:
		return render_template('page/page_not_found.htm', page=page_path)

	old_page = Page.query.filter(Page.path==page_path).first()

	if not old_page:
		return render_template('page/page_not_found.htm', page=page_path)

	revision, page = retrieve_page(page_path)

	if not revision:
		return render_template('page/page_not_found.htm', page=page_path)

	if form.validate_on_submit():
		error = False
		if not rights['edit']:
			return redirect(url_for('index'))

		new_path = form.path.data.strip().strip('/')
		new_page = Page.query.filter(Page.path==new_path).first()

		if page_path == new_path:
			flash('Path stayed the same', 'success')

		elif new_page:
			flash('The path already exists', 'error')
			error = True

		else:
			old_page.path = new_path

		if form.move_children.data and not error:
			# Move this and children
			print 'bla'
			prefix = page_path + '/'
			children = Page.query.filter(Page.path.startswith(prefix)).all()
			for child in children:
				new_child_path = new_path + child.path[len(page_path):]

				if Page.query.filter(Page.path==new_child_path).first():
					db.session.rollback()
					flash('The subpath ' + new_child_path + ' already exists',
							  'error')
					error = True
					break

				child.path = new_child_path


		if not error:
			db.session.commit()
			return redirect(url_for('page.view_page', page_path=new_path))


	flash_form_errors(form)

	return render_template('page/view_page.htm', revision=revision,
		page=page_path, rights=rights, form=form)

def retrieve_page(page_path=''):
	page = Page.query.filter(Page.path==page_path).first()

	if not page:
		return False

	revision = page.get_most_recent_revision()

	if not revision:
		return False

	return revision, page


@page_module.route('/page/delete/')
@page_module.route('/page/delete/<path:page_path>')
def delete_page(page_path='', revision=''):
	page = Page.query.filter(Page.path==page_path).first()
	revisions = PageRevision.query.filter(PageRevision.page_id==page.id).all()
	for revision in revisions:
		db.session.delete(revision)
	db.session.delete(page)
	db.session.commit()
	return redirect('/')

@page_module.route('/page/edit/', methods=['GET', 'POST'])
@page_module.route('/page/edit/<path:page_path>', methods=['GET', 'POST'])
def edit_page(page_path=''):
	if not PagePermission.get_user_rights(current_user, page_path)['edit']:
		return redirect(url_for('index'))

	page = Page.query.filter(Page.path==page_path).first()
	revision = None

	if page:
		revision = page.get_most_recent_revision()

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

		return redirect(url_for('page.view_page', page_path=page_path))

	return render_template('page/edit_page.htm', revision=revision, page=page_path)

