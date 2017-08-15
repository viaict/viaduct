from flask_login import current_user
from app.models.page import PagePermission
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import os

from flask import render_template

from app.models.group import Group
from app.utils.file import file_exists_pattern, file_remove_pattern, \
    file_upload


ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
UPLOAD_DIR = 'app/static/files/users/'


class UserAPI:
    @staticmethod
    def has_avatar(user_id):
        """Check if the user has uploaded an avatar."""
        return bool(file_exists_pattern('avatar_' + str(user_id) + '.*',
                    UPLOAD_DIR))

    @staticmethod
    def remove_avatar(user):
        """Remove avatar of a user."""
        # Find avatar by avatar_<userid>.*
        file_remove_pattern('avatar_' + str(user.id) + '.*', UPLOAD_DIR)

    @staticmethod
    def avatar(user):
        """Return the avatar of the user.

        # If the user uploaded a avatar return it.
        If the user did not upload an avatar checks if the user has an
        gravatar, if so return that.
        If the user neither has an avatar nor an gravatar return default image.
        """

        # check if user has avatar if so return it
        avatar = file_exists_pattern('avatar_' + str(user.id) + '.*',
                                     UPLOAD_DIR)

        if avatar:
            return '/static/files/users/' + avatar

        # Set default values gravatar
        email = user.email or ''
        default = 'identicon'
        size = 100

        # Construct the url
        gravatar_url = 'https://www.gravatar.com/avatar/' +\
            hashlib.md5(email.lower().encode('utf-8')).hexdigest() + '?'
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    @staticmethod
    def upload(f, user_id):
        """Upload the new avatar.

        Checks if the file type is allowed if so removes any
        previous uploaded avatars.
        """
        # Remove old avatars
        file_remove_pattern('avatar_' + str(user_id) + '.*', UPLOAD_DIR)

        # construct file name
        filename = 'avatar_' + str(user_id) + '.' + \
                   os.path.split(f.filename)[1]

        # Save new avatar
        file_upload(f, UPLOAD_DIR, True, filename)

    @staticmethod
    def get_groups_for_user_id(user):
        """Return all the groups the current user belongs in.

        If there is no current_user (no sign in), all is returned if guests
        exists, otherwise it crashes because there can not be no all.

        I believe we cant put this in user because current_user can be None if
        there is no user currently logged in, but I might be mistaken. (Inja
        july 10 2013).
        """
        if not user or not user.id:
            group = Group.query.filter(Group.name == 'all').first()

            if not(group):
                raise Exception("No group 'guests', this should never happen!")
            return [group]

        return user.groups

    @staticmethod
    def get_groups_for_current_user():
        """Call the get_groups_for_user_id function with current user."""
        return UserAPI.get_groups_for_user_id(current_user)

    @staticmethod
    def can_read(page):
        if page.needs_paid and (current_user.is_anonymous or
                                not current_user.has_paid):
            return False

        return PagePermission.get_user_rights(current_user, page) > 0

    @staticmethod
    def can_write(page):
        return PagePermission.get_user_rights(current_user, page) > 1

    @staticmethod
    def get_membership_warning():
        """Render a warning if the current user has not paid."""
        if current_user.is_anonymous or\
                (current_user.is_authenticated and
                    (current_user.has_paid or current_user.alumnus)):
            return ''

        return render_template('user/membership_warning.htm')
