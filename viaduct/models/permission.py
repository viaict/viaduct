#!/usr/bin/python

from viaduct import db

class Permission(db.Model):
	__tablename__ = 'permission'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	label = db.Column(db.String(64))

class UserPermission(db.Model):
	__tablename__ = 'user_permission'

	id = db.Column(db.Integer, primary_key=True)
	permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	allowed = db.Column(db.Boolean)

	permission = db.relationship('Permission', backref=db.backref('user_permissions', lazy='dynamic'))
	user = db.relationship('User', backref=db.backref('permissions', lazy='dynamic'))

	def __init__(self, user, permission, allowed=True):
		self.user_id = user.id
		self.permission_id = permission.id
		self.allowed = allowed

class GroupPermission(db.Model):
	__tablename__ = 'group_permission'

	id = db.Column(db.Integer, primary_key=True)
	permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	allowed = db.Column(db.Boolean)

	permission = db.relationship('Permission', backref=db.backref('group_permissions', lazy='dynamic'))
	group = db.relationship('Group', backref=db.backref('permissions', lazy='dynamic'))

	def __init__(self, group, permission, allowed=True):
		self.group_id = group.id
		self.permission_id = permission.id
		self.allowed = allowed

