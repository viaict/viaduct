from viaduct import db

class NavigationEntry(db.Model):
	__tablename__ = 'nagivation_entry'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('nagivation_entry.id'))
	title = db.Column(db.String(256))
	url = db.Column(db.String(256))
	external = db.Column(db.Boolean)

	parent = db.relationship('NavigationEntry', remote_side=[id],
            primaryjoin=('NavigationEntry.parent_id==NavigationEntry.id'),
            backref="children")

	def __init__(self, parent, title, url, external):
		if parent:
			self.parent_id = parent.id

		self.title = title
		self.url = url
		self.external = external

	def __repr__(self):
		return '<NavigationEntry(%s, %s, "%s", "%s", %s)>' % (self.id,
				self.parent_id, self.title, self.url, self.external)

	@classmethod
	def get_entries(cls):
		return db.session.query(cls).filter_by(parent_id=None).all()
