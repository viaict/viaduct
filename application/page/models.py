import datetime
from sqlalchemy import desc

from application import db

class Page(db.Model):
	__tablename__ = 'page'

	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String(256), unique=True)
	revisions = db.relationship('PageRevision', backref='page', lazy='dynamic')

	def __init__(self, path):
		self.path = path

	def get_most_recent_revision(self):
		return PageRevision.query.filter(PageRevision.page_id==self.id).order_by(PageRevision.timestamp.desc()).first()

class PageRevision(db.Model):
	__tablename__ = 'page_revision'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128))
	content = db.Column(db.Text)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	page_id = db.Column(db.Integer, db.ForeignKey('page.id'))

	def __init__(self, page, author, title, content,
		timestamp=datetime.datetime.utcnow()):
		self.title = title
		self.path = ''
		self.content = content
		self.user_id = author.id
		self.page_id = page.id
		self.timestamp = timestamp

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
	def get_rights(user, page_path):
		rights = []
		groups = user.groups.all()

		for group in groups:
			current_path = page_path

			while True:
				page = Page.query.filter(Page.path==current_path)

				if page:
					permissions = group.page_permissions.filter(Page.id==page.id).first()

					if permissions:
						if permissions.view and not 'view' in rights:
							rights.append('view')

						if permissions.create and not 'create' in rights:
							rights.append('create')

						if permissions.edit and not 'edit' in rights:
							rights.append('edit')

						if permissions.delete and not 'delete' in rights:
							rights.append('delete')

						break

				if len(current_path) == 0:
					break

				if not '/' in current_path:
					current_path = ''
				else:
					current_path = current_path.rsplit('/', 1)[0]

		return rights

