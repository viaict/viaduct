from flask import request

from app.models.page import Page, PageRevision
from app.roles import Roles
from app.service import role_service


# Get the guide page for a specific module
# There is an admin and user page available, dependent on the
# rights of the user
class GuideAPI:

    @staticmethod
    def get_current_user_guide():
        module_name = request.blueprint

        """ Get the user guide for a specific module """
        user_guide = Page.get_by_path('guides/user/' + module_name)

        if not user_guide:
            user_revision = PageRevision(None, None, None, None, None, None,
                                         None)
            user_revision.title = \
                'Er is geen user handleiding beschikbaar voor ' + module_name

            if role_service.user_has_role(Roles.PAGE_WRITE):
                user_revision.content = 'Voeg ' +\
                    '<a href="/edit/guides/user/' + module_name + \
                    '"> hier </a> een user handleiding toe.'
            else:
                user_revision.content = ''
        else:
            user_revision = user_guide.get_latest_revision()
            if role_service.user_has_role(Roles.PAGE_WRITE):
                user_revision.title += '<a href="/edit/guides/user/' +\
                    module_name + '"> (bewerk) </a>'

        return user_revision

    @staticmethod
    def get_current_admin_guide():
        module_name = request.blueprint

        admin_guide = Page.get_by_path('guides/admin/' + module_name)

        if not admin_guide:
            admin_revision = PageRevision(None, None, None, None, None, None,
                                          None)
            admin_revision.title = \
                'Er is geen admin handleiding beschikbaar voor ' + \
                module_name
            if role_service.user_has_role(Roles.PAGE_WRITE):
                admin_revision.content = 'Voeg ' +\
                    '<a href="/edit/guides/admin/' + module_name +\
                    '"> hier </a> een admin handleiding toe.'
            else:
                admin_revision.content = ''

        else:
            admin_revision = admin_guide.get_latest_revision()
            if role_service.user_has_role(Roles.PAGE_WRITE):
                admin_revision.title += '<a href="/edit/guides/admin/' + \
                    module_name + '"> (bewerk) </a>'

        return admin_revision
