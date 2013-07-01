#!/usr/bin/python

from viaduct import db, login_manager
from viaduct.models import GroupPermission, Permission, UserPermission

class User(db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), unique=True)
	password = db.Column(db.String(60))
	first_name = db.Column(db.String(256))
	last_name = db.Column(db.String(256))
	student_id = db.Column(db.String(256))

	def __init__(self, email=None, password=None, first_name=None, last_name=None, student_id=None):
		if not email:
			self.id = 0

		self.email = email
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
		self.student_id = student_id

	def is_authenticated(self):
		return self.id != 0

	def is_active(self):
		return self.id != 0

	def is_anonymous(self):
		return self.id == 0

	def get_id(self):
		return unicode(self.id)

	def get_student_id(self):
		return self.student_id

	@staticmethod
	def get_anonymous_user():
		return User.query.get(0);

	def has_user_permission(self, name):
		permission = self.permissions.join(Permission).filter(Permission.name==name).order_by(UserPermission.allowed.desc()).first()

		if not permission:
			return 0

		if permission.allowed:
			return 1
		else:
			return -1

	def has_permission(self, name):
		# Check if the permission has been allowed to or denied from the user.
		permission = self.permissions.join(Permission).filter(Permission.name==name).order_by(UserPermission.allowed.desc()).first()

		if permission:
			return permission.allowed

		# Check if the permission has been allowed to or denied from any groups
		# associated with the user.
		permission = self.groups.join(GroupPermission).join(Permission).filter(Permission.name==name).order_by(GroupPermission.allowed.desc()).first()

		if permission:
			return permission.allowed

		# Assume the permission has been denied from the user.
		return False

	def add_permission(self, name, allowed=True):
		# Clean up all previous permissions.
		self.delete_permission(name)

		# Set the permission for the user.
		permission = Permission.query.filter(Permission.name==name).first()
		db.session.add(UserPermission(self, permission, allowed))
		db.session.commit()

	def delete_permission(self, name):
		for permission in self.permissions.join(Permission).filter(Permission.name==name).all():
			db.session.delete(permission)

		db.session.commit()

	def __repr__(self):
		return '<User({0}, "{1}", "{2}", "{3}", "{4}", "{5}">'.format(self.id,
				self.email, self.password, self.first_name, self.last_name,
				self.student_id)

