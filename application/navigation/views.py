from flask import Markup
from flask import render_template

from application import db
from application.page.models import Page

def find_subpages(list_pages, page):
	subpages = []
	prefix = page.split('/')[0]
	
	for subpage in list_pages:
		if subpage.path.split('/')[0] == prefix:
			subpages += [subpage]
            
	return subpages

def view_bar(current_page=''):
	pages = Page.query.all()

	#if len(current_page) == 0:
	#	return 'TODO: what?'

	subpages = find_subpages(pages, current_page)
	
	return Markup(render_template('navigation/view_bar.htm', subpages=subpages, page=current_page))

