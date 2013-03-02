from application import db
from application.user.models import User, UserPermission

user_group = db.Table('user_group',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class Group(db.Model):
	__tablename__ = 'group'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(256), unique=True)
	users = db.relationship('User', secondary=user_group,
		backref=db.backref('groups', lazy='dynamic'), lazy='dynamic')
	user_permissions = db.relationship('UserPermission', uselist=False,
		backref='group')
	group_permissions = db.relationship('GroupPermission', uselist=False,
		backref='group')
	page_permissions = db.relationship('PagePermission', backref='group',
		lazy='dynamic')

	def __init__(self, name):
		self.name = name

	def has_user(self, user):
		return self.users.filter(user_group.c.user_id == user.id).count() > 0
	
	def add_user(self, user):
		if not self.has_user(user):
			self.users.append(user)

			return self

	def delete_user(self, user):
		if self.has_user(user):
			self.users.remove(user)

			return self

	def get_users(self):
		return User.query.join(user_group, (user_group.c.user_id == User.id)).filter(user_group.c.group_id == self.id)

class GroupPermission(db.Model):
	__tablename__ = 'group_permission'

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
		permissions = group.group_permissions

		if permissions:
			rights['view'] = permissions.view
			rights['create'] = permissions.create
			rights['edit'] = permissions.edit
			rights['delete'] = permissions.delete

		return rights

	@staticmethod
	def get_user_rights(user):
		rights = {'view': False, 'create': False, 'edit': False,
			'delete': False}
		groups = user.groups.all()

		for group in groups:
			permissions = group.group_permissions

			if permissions:
				rights['view'] = rights['view'] or permissions.view
				rights['create'] = rights['create'] or permissions.create
				rights['edit'] = rights['edit'] or permissions.edit
				rights['delete'] = rights['delete'] or permissions.delete

		return rights

