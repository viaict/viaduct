from application import db

class User(db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), unique=True)
	password = db.Column(db.String(60))
	first_name = db.Column(db.String(256))
	last_name = db.Column(db.String(256))
	page_edits = db.relationship('PageRevision', backref='author',
		lazy='dynamic')

	def __init__(self, email, password, first_name, last_name):
		self.email = email
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
	
	def is_authenticated(self):
		return self.email != 'anonymous'

	def is_active(self):
		return self.email != 'anonymous'

	def is_anonymous(self):
		return self.email == 'anonymous'

	def get_id(self):
		return unicode(self.id)

class UserPermission(db.Model):
	__tablename__ = 'user_permission'

	id = db.Column(db.Integer, primary_key=True)
	view = db.Column(db.Boolean)
	create = db.Column(db.Boolean)
	edit = db.Column(db.Boolean)
	delete = db.Column(db.Boolean)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

	def __init__(self, group, view=False, create=False, edit=False,
		delete=False):
		self.view = view
		self.create = create
		self.edit = edit
		self.delete = delete
		self.group_id = group.id

	@staticmethod
	def get_rights(user):
		rights = []
		groups = user.groups.all()

		for group in groups:
			permissions = group.user_permissions

			if permissions:
				if permissions.view and not 'view' in rights:
					rights.append('view')

				if permissions.create and not 'create' in rights:
					rights.append('create')

				if permissions.edit and not 'edit' in rights:
					rights.append('edit')

				if permissions.delete and not 'delete' in rights:
					rights.append('delete')

		return rights

