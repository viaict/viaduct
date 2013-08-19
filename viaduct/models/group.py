#!/usr/bin/python

from viaduct import db
from viaduct.models.permission import GroupPermission

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

	def __init__(self, name):
		self.name = name

	def has_user(self, user):
		if not user:
			return False;
		else:
			return self.users.filter(user_group.c.user_id==user.id).count() > 0

	def add_user(self, user):
		if not self.has_user(user):
			self.users.append(user)

			return self

	def delete_user(self, user):
		if self.has_user(user):
			self.users.remove(user)

	def get_users(self):
		# FIXME: backwards compatibility.
		return self.users

	#def get_permission(self, name):
	#	permission = self.permissions.join(Permission).filter(Permission.name==name).order_by(GroupPermission.allowed.desc()).first()

	#	if not permission:
	#		return 0

	#	if permission.allowed:
	#		return 1
	#	else:
	#		return -1

	#def has_permission(self, name):
	#	permission = self.permissions.join(Permission).filter(Permission.name==name).order_by(GroupPermission.allowed.desc()).first()

	#	if permission:
	#		return permission.allowed

	#	return False
	#
	#def add_permission(self, name, allowed=True):
	#	self.delete_permission(name)

	#	permission = Permission.query.filter(Permission.name==name).first()
	#	db.session.add(GroupPermission(self, permission, allowed))
	#	db.session.commit()

	#def delete_permission(self, name):
	#	for permission in self.permissions.join(Permission).filter(Permission.name==name).all():
	#		db.session.delete(permission)

	#	db.session.commit()

