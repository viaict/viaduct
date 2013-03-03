from flask import Markup
from flask import render_template

from application.page.models import Page
from application.helpers import find_subpages, get_current_page

def view_bar():
	current_page = get_current_page().split('/')[0]
	pages = Page.get_all_pages()
	all_pages = []
	pages.sort()


	for page in pages:
		if not '/' in page.path:
			all_pages.append({'main': page,
				'subpages': find_subpages(pages, page)})

	return Markup(render_template('navigation/view_bar.htm', pages=all_pages,
								  current_page=current_page))

def view_side_bar():
	current_page = get_current_page()
	level = current_page.count('/')
	children = Page.get_children('/'.join(current_page.split('/')[:level + 1]))
	if level > 0:
		sibblings = Page.get_children('/'.join(current_page.split('/')[:level]))
	else:
		sibblings = children

	sibblings.sort()
	children.sort()

	return Markup(render_template('navigation/sidenav.htm',
								  sibblings=sibblings,
								  children=children,
								  current_page=current_page))
