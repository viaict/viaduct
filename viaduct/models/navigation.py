from viaduct import db
from viaduct.blueprints.activity.models import Activity

import datetime

class NavigationEntry(db.Model):
	__tablename__ = 'nagivation_entry'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
	title = db.Column(db.String(256))
	url = db.Column(db.String(256))
	external = db.Column(db.Boolean)
	activity_list = db.Column(db.Boolean)
	position = db.Column(db.Integer)

	parent = db.relationship('NavigationEntry', remote_side=[id],
            primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
            backref="children")

	def __init__(self, parent, title, url, external, activity_list, position):
		if parent:
			self.parent_id = parent.id

		self.title = title
		self.url = url
		self.external = external
		self.activity_list = activity_list
		self.position = position

	def __repr__(self):
		return '<NavigationEntry(%s, %s, "%s", "%s", %s)>' % (self.id,
				self.parent_id, self.title, self.url, self.external)

	@classmethod
	def get_entries(cls):
		entries = db.session.query(cls).filter_by(parent_id=None)\
				.order_by(cls.position).all()

		# Fill in activity lists.
		for entry in entries:
			if entry.activity_list:
				entry.children = []
				activities = db.session.query(Activity)\
						.filter(Activity.end_time > datetime.datetime.now())\
						.all()

				for activity in activities:
					entry.children.append(NavigationEntry(entry, activity.name,
							'/activity/' + str(activity.id), False, False))

		return entries
