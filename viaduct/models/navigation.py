from viaduct import db

class NavigationEntry(db.Model):
	__tablename__ = 'nagivation_entry'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
	url = db.Column(db.String(256))
	external = db.Column(db.Boolean)

	parent = db.relationship('NavigationEntry', remote_side=[id],
            primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
            backref=db.backref("right", uselist=False))

	def __init__(self, parent, url, external):
		if parent:
			self.parent_id = parent.id

		self.url = url
		self.external = external

	def __repr__(self):
		return '<NavigationEntry(%s, %s, "%s", %s)>' % (self.id,
				self.parent_id, self.url, self.external)
