import datetime

from viaduct import db

page_ancestor = db.Table('page_ancestor',
	db.Column('page_id', db.Integer, db.ForeignKey('page.id')),
	db.Column('ancestor_id', db.Integer, db.ForeignKey('page.id'))
)

class Page(db.Model):
	__tablename__ = 'page'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('page.id'))
	path = db.Column(db.String(256), unique=True)

	parent = db.relationship('Page',
			remote_side=id,
			backref=db.backref('children', lazy='dynamic'))
	ancestors = db.relationship('Page', secondary=page_ancestor,
		primaryjoin=id==page_ancestor.c.page_id,
		secondaryjoin=id==page_ancestor.c.ancestor_id,
		backref=db.backref('descendants', lazy='dynamic'), lazy='dynamic')
	revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

	def __init__(self, path):
		self.path = path

	def __repr__(self):
		return '<Page(%s, "%s")>' % (self.id, self.path)

	@staticmethod
	def get_by_path(path):
		return Page.query.filter(Page.path==path).first()

	def has_revisions(self):
		return self.revisions.count() > 0

	def get_newest_revision(self):
		return self.revisions.order_by(PageRevision.timestamp.desc()).first()

class PageRevision(db.Model):
	__tablename__ = 'page_revision'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	filter_html = db.Column(db.Boolean)
	content = db.Column(db.Text)
	comment = db.Column(db.String(1024))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

	author = db.relationship('User', backref=db.backref('page_edits',
		lazy='dynamic'))

	def __init__(self, page, author, title, content, comment="", filter_html=True,
			timestamp=datetime.datetime.utcnow()):
		self.title = title
		self.content = content
		self.comment = comment
		self.filter_html = filter_html
		self.user_id = author.id
		self.page_id = page.id
		self.timestamp = timestamp

class PagePermission(db.Model):
	__tablename__ = 'page_permission'

	id = db.Column(db.Integer, primary_key=True)
	view = db.Column(db.Boolean)
	create = db.Column(db.Boolean)
	safe_edit = db.Column(db.Boolean)
	unsafe_edit = db.Column(db.Boolean)
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
		rights = {'view': False, 'create': False, 'safe_edit': False,
			'unsafe_edit': False, 'delete': False}
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
						rights['safe_edit'] = rights['safe_edit'] or permissions.safe_edit
						rights['unsafe_edit'] = rights['unsafe_edit'] or permissions.unsafe_edit
						rights['delete'] = rights['delete'] or permissions.delete

						break

				if len(current_path) == 0:
					break

				if not '/' in current_path:
					current_path = ''
				else:
					current_path = current_path.rsplit('/', 1)[0]

		return rights

