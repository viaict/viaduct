from flask import Markup
from flask import render_template, request

from viaduct.blueprints.page.models import Page

class NavigationAPI:
	@staticmethod
	def get_navigation_bar():
		path = request.path
		pages = Page.query.filter(Page.revisions).all()
		all_pages = []

		for page in pages:
			children = page.children.all()

			all_pages.append({'current': page, 'children': children})

		return Markup(render_template('navigation/api/get_navigation_bar.htm',
			pages=all_pages, path=path))

		return ''

	@staticmethod
	def get_navigation_menu():
		path = request.path
		page = Page.query.filter(Page.path==path).first()

		if not page:
			return ''

		children = page.children.order_by(Page.title).all()
		siblings = Page.query.filter(Page.parent_id==parent.id).order_by(Page.title).all()

		return Markup(render_template('navigation/get_navigation_menu.htm',
			page=page, children=children, siblings=siblings, path=path))

