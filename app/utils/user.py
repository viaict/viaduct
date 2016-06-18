from flask.ext.login import current_user
from app.models.page import PagePermission
from flask import flash
import os
import fnmatch
import urllib.request
import urllib.parse
import urllib.error
import hashlib

from flask import render_template

from app.models.group import Group
from app.utils.file import FileAPI

from flask.ext.babel import lazy_gettext as _

ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
UPLOAD_DIR = 'app/static/files/users/'


class UserAPI:
    @staticmethod
    def has_avatar(user_id):
        """Check if the user has uploaded an avatar."""
        for file in os.listdir(UPLOAD_DIR):
            if fnmatch.fnmatch(file, 'avatar_' + str(user_id) + '.*'):
                return True
        return False

    @staticmethod
    def remove_avatar(user):
        """Remove avatar of a user."""
        # Find avatar by avatar_<userid>.*
        for file in os.listdir(UPLOAD_DIR):
            if fnmatch.fnmatch(file, 'avatar_' + str(user.id) + '.*'):
                path = UPLOAD_DIR + file
                os.remove(path)

    @staticmethod
    def avatar(user):
        """Return the avatar of the user.

        If the user uploaded a avatar return it.
        If the user did not upload an avatar checks if the user has an
        gravatar, if so return that.
        If the user neither has an avatar nor an gravatar return default image.
        """

        # check if user has avatar if so return it
        for file in os.listdir(UPLOAD_DIR):
            if fnmatch.fnmatch(file, 'avatar_' + str(user.id) + '.*'):
                path = '/static/files/users/' + file
                return(path)

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
        filename = f.filename

        # Check if the file is allowed.
        if filename == '':
            return

        if '.' not in filename or not filename.rsplit('.', 1)[1].lower() \
                in ALLOWED_EXTENSIONS:
            flash(_('Filetype not allowed'), 'danger')
            return

        # convert the name.
        filename = 'avatar_%d.%s' % (user_id, filename.rsplit('.', 1)[1])
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

        return user.groups.order_by(Group.name)

    @staticmethod
    def get_groups_for_current_user():
        """Call the get_groups_for_user_id function with current user."""
        return UserAPI.get_groups_for_user_id(current_user)

    @staticmethod
    def can_read(page):
        if page.needs_payed and (not current_user or
                                 not current_user.has_payed):
            return False

        return PagePermission.get_user_rights(current_user, page.id) > 0

    @staticmethod
    def can_write(page):
        return PagePermission.get_user_rights(current_user, page.id) > 1

    @staticmethod
    def get_membership_warning():
        """Render a warning if the current user has not payed."""
        if not current_user or current_user.id == 0 or \
                current_user.has_payed:
            return ''

        return render_template('user/membership_warning.htm')
