from flask import render_template

from viaduct.models.navigation import NavigationEntry

class NavigationAPI:

	@staticmethod
	def get_navigation_bar():
		entries = NavigationEntry.get_entries()
		return render_template('navigation/view_bar.htm', entries=entries)

	@staticmethod
	def get_navigation_menu():
		return render_template('navigation/view_sidebar.htm', pages=[])
