from flask.ext.login import current_user

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
		if current_user == None:
			group = Group.query.filter(Group.name=='all').first()
			if not(group):
				raise Exception("No group 'guests', this should never happen!")
			return [group]
		return current_user.groups
