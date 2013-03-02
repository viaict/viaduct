from flask import Markup
from flask import render_template

from application import db
from application.page.models import Page

def find_subpages(pages, parent):
	subpages = []

	for pages in list_pages:
		prefix = '/'.join(pages.split('/')[:-1])
		if prefix == parent.path:
			subpages.append(subpage)

	return subpages

def view_bar(current_page=''):
	print 'bla'
	print Page.query.all()
	print 'bloe'
	all_pages = map(lambda x: x.get_most_recent(), Page.query.all())
	pages = []
	print all_pages
	mainpages = filter(lambda x: '/' not in x.path, all_pages)

	#if len(current_page) == 0:
	#	return 'TODO: what?'

	for page in mainpages:
		pages.append({main: page,
					  subpages: findsubpages(all_pages, page)})


	return Markup(render_template('navigation/view_bar.htm', pages=pages, current_page=current_page))

