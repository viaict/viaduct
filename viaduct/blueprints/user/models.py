from viaduct import db

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
	def get_group_rights(group):
		rights = {'view': False, 'create': False, 'edit': False,
			'delete': False}
		permissions = group.user_permissions

		if permissions:
			rights['view'] = permissions.view
			rights['create'] = permissions.create
			rights['edit'] = permissions.edit
			rights['delete'] = permissions.delete

		return rights

	@staticmethod
	def set_group_rights(group, rights):
		permissions = group.user_permissions

		if not permissions:
			permissions = UserPermission(rights['view'], rights['create'],
				rights['edit'], rights['delete'])
		else:
			permissions.view = rights['view']
			permissions.create = rights['create']
			permissions.edit = rights['edit']
			permissions.delete = rights['delete']

		db.session.add(permissions)
		db.session.commit()

	@staticmethod
	def get_user_rights(user):
		rights = {'view': False, 'create': False, 'edit': False,
			'delete': False}
		groups = user.groups.all()

		for group in groups:
			permissions = group.user_permissions

			if permissions:
				rights['view'] = rights['view'] or permissions.view
				rights['create'] = rights['create'] or permissions.create
				rights['edit'] = rights['edit'] or permissions.edit
				rights['delete'] = rights['delete'] or permissions.delete

		return rights

