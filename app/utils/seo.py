import re

from flask import request

from app.models import Page, SEO, Activity
from app.utils import Resource


class SeoAPI(Resource):
    # API for retrieving seo information of pages

    """ Get the seo fields as dict"""
    @staticmethod
    def get_seo_fields(language='nl', module_name=None, request_path=None):
        # Check if the module and path are set.
        if module_name is None:
            module_name = request.blueprint

        if request_path is None:
            request_path = request.path

        # Check which type of seo fields should be retrieved, based on
        # the module name.
        if module_name == "activity":
            # Get activity id
            activity_id = re.search(r'\/([0-9]+)\/', request_path)

            # Check seo existance
            if activity_id is not None:
                # Get the seo object of an activity
                seo = SEO.get_by_activity(activity_id.group(1))
            else:
                # No seo was found for this activity
                seo = None

        elif module_name == "page":
            # Retrieve the page for its id
            path = request_path[1:]
            page = Page.get_by_path(path)

            # Retrieve the revision by page id
            if page is not None:
                seo = SEO.get_by_page(page.id)
            else:
                seo = None
        else:
            # Retrieve seo fields based on the module name.
            seo = SEO.get_by_url(module_name)

        # Retrieve the seo fields based on the seo object
        # or global set values.
        if seo is not None:

            # Retrieve the language specific SEO fields
            if language == 'nl':
                return {'title': seo.nl_title,
                        'description': seo.nl_description,
                        'tags': seo.nl_tags}
            elif language == 'en':
                return {'title': seo.en_title,
                        'description': seo.en_description,
                        'tags': seo.en_tags}
        else:
            # TODO, good standard tags
            return {'title': 'via',
                    'description': 'Studievereniging via - Informatica, ' +
                                   'Informatiekunde, Informatica, ' +
                                   'University of Amsterdam',
                    'tags': 'Studievereniging,via, informatica, ' +
                            'informatiekunde, University of Amsterdam'}

    """ Attempt to retrieve seo object, None otherwise """
    def get_seo(module_name=None, request_path=None):
        # Check if the module and path are set.
        if module_name is None:
            module_name = request.blueprint

        if request_path is None:
            request_path = request.path

        # Check which type of seo fields should be retrieved, based on
        # the module name.
        if module_name == "activity":
            # Get activity id
            activity_id = re.search(r'\/([0-9]+)\/', request_path)

            # Check seo existance
            if activity_id is not None:
                # Get the seo object of an activity
                return SEO.get_by_activity(activity_id.group(1))
            else:
                # No seo was found for this activity
                return None

        elif module_name == "page":
            # Retrieve the page for its id
            path = request_path[1:]
            page = Page.get_by_path(path)

            # Retrieve the revision by page id
            if page is not None:
                return SEO.get_by_page(page.id)
            else:
                return None
        else:
            # Retrieve seo fields based on the module name.
            seo = SEO.get_by_url(module_name)

            return seo

        return None

    @staticmethod
    def get_resources(module_name=None, request_path=None):
        # Check if the module and path are set.
        if module_name is None:
            module_name = request.blueprint

        if request_path is None:
            request_path = request.path

        # Empty resources for all resources that are not retrieved.
        page = None
        page_id = None
        activity = None
        activity_id = None
        path = None

        # Check which type of seo fields should be retrieved, based on
        # the module name.
        if module_name == "activity":
            # Regex search for acitivity id
            activity_result = re.search(r'\/([0-9]+)\/', request_path)

            # Fetch id from regex
            activity_id = activity_result.group(1)

            # Find activity
            activity = Activity.query.filter(Activity.id ==
                                             activity_id).first()
            print("lalalala")

        elif module_name == "page":
            # Retrieve the page for its id
            path = request_path[1:]
            page = Page.get_by_path(path)

            # Retrieve the revision by page id
            if page is not None:
                page_id = page.id
                print("lalala")
        else:
            # Retrieve seo fields based on the module name.
            path = module_name

        return {'page': page, 'page_id': page_id,
                'activity': activity, 'activity_id': activity_id,
                'url': path}
