import datetime

from viaduct import db

class PageAncestor(db.Model):
	__tablename__ = 'page_ancestor'

	page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
	ancestor_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)

class Page(db.Model):
	__tablename__ = 'page'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer)
	title = db.Column(db.String(128))
	path = db.Column(db.String(256), unique=True)
	#parent = db.relationship('Page', remote_side=[id])
	ancestors = db.relationship('PageAncestor',
		primaryjoin=id==PageAncestor.ancestor_id,
		backref=db.backref('descendants', lazy='dynamic'), lazy='dynamic')
	revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

	def __init__(self, path):
		self.path = path
	
	def __repr__(self):
		return '<Page(%s, "%s")>' % (self.id, self.path)

class PageRevision(db.Model):
	__tablename__ = 'page_revision'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	content = db.Column(db.Text)
	priority = db.Column(db.Integer, default=0)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

	def __init__(self, page, author, title, content, priority,
		timestamp=datetime.datetime.utcnow()):
		self.title = title
		self.content = content
		self.priority = priority
		self.user_id = author.id
		self.page_id = page.id
		self.timestamp = timestamp
		self.path = ''

class PagePermission(db.Model):
	__tablename__ = 'page_permission'

	id = db.Column(db.Integer, primary_key=True)
	view = db.Column(db.Boolean)
	create = db.Column(db.Boolean)
	edit = db.Column(db.Boolean)
	delete = db.Column(db.Boolean)
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

	def __init__(self, group, page, view=False, create=False, edit=False,
		delete=False):
		self.view = view
		self.create = create
		self.edit = edit
		self.delete = delete
		self.group_id = group.id
		self.page_id = page.id

	@staticmethod
	def get_user_rights(user, page_path):
		rights = {'view': False, 'create': False, 'edit': False,
			'delete': False}
		groups = user.groups.all()

		for group in groups:
			current_path = page_path

			while True:
				page = Page.query.filter(Page.path==current_path).first()

				if page:
					permissions = group.page_permissions.filter(Page.id==page.id).first()

					if permissions:
						rights['view'] = rights['view'] or permissions.view
						rights['create'] = rights['create'] or permissions.create
						rights['edit'] = rights['edit'] or permissions.edit
						rights['delete'] = rights['delete'] or permissions.delete

						break

				if len(current_path) == 0:
					break

				if not '/' in current_path:
					current_path = ''
				else:
					current_path = current_path.rsplit('/', 1)[0]

		return rights

