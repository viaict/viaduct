from flask import render_template, request

from viaduct.models.navigation import NavigationEntry

class NavigationAPI:

	@staticmethod
	def get_navigation_bar():
		entries = NavigationEntry.get_entries()
		return render_template('navigation/view_bar.htm', entries=entries)

	@staticmethod
	def get_navigation_menu():
		first_part = "/" + request.path.split('/')[1]
		page = NavigationEntry.query.filter(NavigationEntry.url == first_part).first()
		print first_part
		pages = []

		if page:
			if page.parent:
				pages = page.parent.children
			elif page.children:
				pages = page.children

		# geen parent -> is top level (wel parent, children van die parent + zichzelf)
		return render_template('navigation/view_sidebar.htm', pages=pages, current=first_part)
