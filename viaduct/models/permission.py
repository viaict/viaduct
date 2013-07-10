#!/usr/bin/python

from viaduct import db

#class Permission(db.Model):
#	__tablename__ = 'permission'
#
#	id = db.Column(db.Integer, primary_key=True)
#	name = db.Column(db.String(64))
#	label = db.Column(db.String(64))
#
#	def __init__(self, name, label):
#		self.name = name
#		self.label = label

#class UserPermission(db.Model):
#	__tablename__ = 'user_permission'
#
#	id = db.Column(db.Integer, primary_key=True)
#	permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	allowed = db.Column(db.Boolean)
#
#	permission = db.relationship('Permission', backref=db.backref('user_permissions', lazy='dynamic'))
#	user = db.relationship('User', backref=db.backref('permissions', lazy='dynamic'))
#
#	def __init__(self, user, permission, allowed=True):
#		self.user_id = user.id
#		self.permission_id = permission.id
#		self.allowed = allowed

class GroupPermission(db.Model):
	"""
	Modules have names, this is not stored or registered, it is simply the name a module
	uses when it checks for permissions of a certain user. In the future we would like
	that modules register themselves so we can keep track of modules in use by the site
	and perhaps make sure that names of modules are unique.

	This class represents a link between a group and a module (name) and adds a permission
	integer: 0 for no rights, 1 for viewing rights, 2 for edit rights.

	Note that if such an entry is absent we can pretend there is actually a 0 (no rights).

	Also note that 2 naturally also means a user can view such a module.

	Finally, we might want to use enums for instead of integers for permisions, but right
	now we just do not care enough for such pretty things.
	"""

	id = db.Column(db.Integer, primary_key=True)
	module_name = db.Column(db.Text)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	group = db.relationship("Group", backref=db.backref('module_permissions',
		lazy='dynamic'))
	permission = db.Column(db.Integer);

	def __init__(self, module_name, group_id, permission):
		"""
		* permission: an integer; 0 for no rights, 1 for viewing rights, 2 for
			edit rights
		"""
		self.module_name = module_name
		self.group_id = group_id
		self.permission = permission


