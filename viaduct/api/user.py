from flask.ext.login import current_user
from viaduct.models.page import Page, PagePermission
from flask import flash
from werkzeug import secure_filename
import os, difflib
import fnmatch
import urllib, hashlib
import inspect

from flask import request, url_for

from viaduct.models.group import Group
from viaduct.api.file import FileAPI

ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
UPLOAD_DIR = 'viaduct/static/files/users/'


class UserAPI:

	@staticmethod
	def avatar(user):
		"""
		Returns users avatar. If the user uploaded a avatar return it.
		If the user did not upload an avatar checks if the user has an
		gravatar, if so return.
		If the user neither has an avatar nor an gravatar return default image.
		"""

		# check if user has avatar if so return it
		for file in os.listdir(UPLOAD_DIR):
			if fnmatch.fnmatch(file, "avatar_" + str(user.id) + '.*'):
				path = '/static/files/users/' + file
				return(path)

		# Set default values gravatar
		email = user.email
		default = 'identicon'
		size = 100

		# Construct the url
		gravatar_url = 'http://www.gravatar.com/avatar/' + hashlib.md5(email.lower()).hexdigest() + '?'
		gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
		return gravatar_url

	@staticmethod
	def upload(f, user_id):
		"""
		Checks if the file type is allowed if so removes any
		previous uploaded avatars.
		Uploads the new avatar
		"""
		filename = f.filename
		# Check if the file is allowed.
		if not '.' in filename or \
				not filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
			flash('Bestandstype is niet toegestaan.')
			return

		# convert the name.
		filename = 'avatar_%d.%s' %(user_id, filename.rsplit('.', 1)[1])
		path = os.path.join(os.getcwd(), UPLOAD_DIR, filename)

		# Check if avatar exists if so remove.
		filename_noext, filename_ext = FileAPI.split_name(filename)

		for file in os.listdir(UPLOAD_DIR):
			if fnmatch.fnmatch(file, filename_noext + '.*'):
				remove_path = os.path.join(os.getcwd(), UPLOAD_DIR, file)
				os.remove(remove_path)

		# Save file.
		f.save(path)
		return

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
		if page.needs_payed and (not current_user or \
								not current_user.has_payed):
			return False

		return PagePermission.get_user_rights(current_user, page.id) > 0

	@staticmethod
	def can_write(page):
		return PagePermission.get_user_rights(current_user, page.id) > 1
