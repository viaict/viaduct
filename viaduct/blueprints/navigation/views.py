from flask import Markup
from flask import render_template

from viaduct.page.models import Page
from viaduct.helpers import find_subpages, get_current_page

def view_bar():
	current_page = request.path.split('/')[0]
	pages = Page.query.filter(Page.revisions).order_by(Page.title).all()
	all_pages = []

	for page in pages:
		children = page.children.all()

		all_pages.append({'main': page,
			'subpages': find_subpages(pages, page)})

	return Markup(render_template('navigation/view_bar.htm', pages=all_pages,
								  current_page=current_page))

def view_side_bar():
	current_page = request.path
	page = Page.query.filter(Page.path==current_page).first()
	children = page.children.order_by(Page.title).all()

	if page.parent:
		siblings = Page.query.filter(Page.parent_id==parent.id).order_by(Page.title).all()
	else:
		siblings = children

	return Markup(render_template('navigation/sidenav.htm',
		siblings=siblings, children=children, current_page=current_page))

