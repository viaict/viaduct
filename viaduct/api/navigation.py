from flask import render_template, request

import datetime

from viaduct import db
from viaduct.blueprints.activity.models import Activity
from viaduct.models.navigation import NavigationEntry

class NavigationAPI:

	@staticmethod
	def get_navigation_bar():
		entries = NavigationEntry.get_entries(True)

		return render_template('navigation/view_bar.htm', bar_entries=entries)


	@staticmethod
	def get_navigation_menu():
		my_path = request.path

		temp_strip = my_path.rstrip('0123456789')
		if temp_strip.endswith('/'):
			my_path = temp_strip

		my_path = my_path.rstrip('/')

		me = db.session.query(NavigationEntry).filter_by(url=my_path)\
				.first()

		if me:
			parent = me.parent
		else:
			parent_path = my_path.rsplit('/', 1)[0]
			parent = db.session.query(NavigationEntry)\
					.filter_by(url=parent_path).first()

		if parent:
			pages = db.session.query(NavigationEntry)\
					.filter_by(parent_id=parent.id)\
					.order_by(NavigationEntry.position).all()
		else:
			pages = [me] if me else []

		return render_template('navigation/view_sidebar.htm', back=parent,
				pages=pages, current=me)

	@staticmethod
	def order(entries, parent):
		position = 1

		for entry in entries:
			db_entry = db.session.query(NavigationEntry)\
					.filter_by(id=entry['id']).first()

			db_entry.parent_id = parent.id if parent else None
			db_entry.position = position

			NavigationAPI.order(entry['children'], db_entry)

			position += 1

			db.session.add(db_entry)
			db.session.commit()
