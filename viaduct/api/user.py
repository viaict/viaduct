from flask.ext.login import current_user
from viaduct.models.page import Page, PagePermission

from flask import request

from viaduct.models.group import Group
import inspect

class UserAPI:

	@staticmethod
	def get_groups_for_current_user():
		"""
		Returns all the groups the current user belongs in.
		If there is no current_user (no sign in), all is returned if guests exists,
		otherwise it crashes because there can not be no all

		I believe we cant put this in user because current_user can be None if there is no
		user currently logged in, but I might be mistaken (Inja july 10 2013)
		"""

		# if there is no user we treat them as if in the guests group
		if not current_user or not current_user.id:
			group = Group.query.filter(Group.name == 'all').first()

			if not(group):
				raise Exception("No group 'guests', this should never happen!")
			return [group]

		return current_user.groups.order_by(Group.name)

	@staticmethod
	def can_read(page):
		print request.url
		return PagePermission.get_user_rights(current_user, page.id) > 0

	@staticmethod
	def can_write(page):
		print request.url
		return PagePermission.get_user_rights(current_user, page.id) > 1
