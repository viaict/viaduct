#!/usr/bin/python

from viaduct import db

class UserPermission(db.Model):
	__tablename__ = 'user_permission'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	name = db.Column(db.String(64))
	allowed = db.Column(db.Boolean)

	user = db.relationship('User', backref=db.backref('permissions', lazy='dynamic'))

	def __init__(self, user, name, allowed=True):
		self.user_id = user.id
		self.name = name
		self.allowed = allowed

class GroupPermission(db.Model):
	__tablename__ = 'group_permission'

	id = db.Column(db.Integer, primary_key=True)
	group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
	name = db.Column(db.String(64))
	allowed = db.Column(db.Boolean)

	group = db.relationship('Group', backref=db.backref('permissions', lazy='dynamic'))

	def __init__(self, group, name, allowed=True):
		self.group_id = group.id
		self.name = name
		self.allowed = allowed

