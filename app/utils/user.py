import hashlib
import urllib.error
import urllib.parse
import urllib.request

from flask import render_template, url_for
from flask_login import current_user

from app.service import user_service

ALLOWED_EXTENSIONS = {'png', 'gif', 'jpg', 'jpeg'}


class UserAPI:

    @staticmethod
    def avatar(user):
        """Return the avatar of the user.

        # If the user uploaded a avatar return it.
        If the user did not upload an avatar checks if the user has an
        gravatar, if so return that.
        If the user neither has an avatar nor an gravatar return default image.
        """

        if user_service.user_has_avatar(user.id):
            return url_for('user.view_avatar', user_id=user.id)

        # Set default values gravatar
        default = 'identicon'
        size = 100
        email = user.email or ''

        # Construct the url
        gravatar_url = 'https://www.gravatar.com/avatar/' + \
                       hashlib.md5(
                           email.lower().encode('utf-8')).hexdigest() + '?'
        gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})
        return gravatar_url

    @staticmethod
    def get_groups_for_user_id(user):
        """Return all the groups the current user belongs in.

        If there is no current_user (no sign in), an empty list is returned.
        """
        if not user or not user.id:
            return []

        return user.groups

    @staticmethod
    def get_groups_for_current_user():
        """Call the get_groups_for_user_id function with current user."""
        return UserAPI.get_groups_for_user_id(current_user)

    @staticmethod
    def get_membership_warning():
        """Render a warning if the current user has not paid."""
        if current_user.is_anonymous or \
                (current_user.is_authenticated and
                 (current_user.has_paid or current_user.alumnus)):
            return ''

        return render_template('user/membership_warning.htm')
