from flask import Markup
from flask import render_template

from application import db, application
from application.page.models import Page

def find_subpages(pages, parent):
	subpages = []

	for page in pages:
		prefix = '/'.join(page.path.split('/')[:-1])
		if prefix == parent.path:
			subpages.append(page)

	return subpages

def view_bar(current_page=''):
	pages = Page.query.all()
	all_pages = []

	for page in pages:
		if not '/' in page.path and page.revisions.count() > 0:
			all_pages.append({'main': page,
				'subpages': find_subpages(pages, page)})

	return Markup(render_template('navigation/view_bar.htm', pages=all_pages, current_page=current_page))

