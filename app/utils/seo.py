import re

from flask import request

from app.models.activity import Activity
from app.models.seo import SEO
from app.service import page_service


###
# TODO PLEASE REFACTOR THIS TO DRY CODE
###

def get_seo_fields(language='nl', module_name=None, request_path=None):
    """Get the seo fields as dict."""
    # Check if the module and path are set.
    if module_name is None:
        module_name = request.blueprint

    if request_path is None:
        request_path = request.path

    seo = None

    # Check which type of seo fields should be retrieved, based on
    # the module name.
    if module_name == "activity":
        # Get activity id
        activity_id = re.search(r'\/([0-9]+)\/', request_path)

        # If activity id found, get the seo object of an activity
        if activity_id is not None:
            seo = SEO.get_by_activity(activity_id.group(1))

    if module_name == "page":
        # Retrieve the page for its id
        path = request_path[1:]
        page = page_service.get_page_by_path(path)

        # Retrieve the revision by page id
        if page is not None:
            seo = SEO.get_by_page(page.id)

    if seo is None:
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


def get_seo(module_name=None, request_path=None):
    """Attempt to retrieve seo object, None otherwise."""
    # Check if the module and path are set.
    if module_name is None:
        module_name = request.blueprint

    if request_path is None:
        request_path = request.path

    seo = None

    # Check which type of seo fields should be retrieved, based on
    # the module name.
    if module_name == "activity":
        # Get activity id
        activity_id = re.search(r'\/([0-9]+)\/', request_path)

        # Get the seo object of an activity
        if activity_id is not None:
            return SEO.get_by_activity(activity_id.group(1))

    if module_name == "page":
        # Retrieve the page for its id
        path = request_path[1:]
        page = page_service.get_page_by_path(path)

        # Retrieve the revision by page id
        if page is not None:
            return SEO.get_by_page(page.id)

    if seo is None:
        # Retrieve seo fields based on the module name.
        seo = SEO.get_by_url(module_name)

        return seo


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

        # Could be overview page.
        if activity_result:

            # Fetch id from regex
            activity_id = activity_result.group(1)

            # Find activity
            activity = Activity.query.filter(Activity.id ==
                                             activity_id).first()

    if module_name == "page":
        # Retrieve the page for its id
        path = request_path.strip('/')
        page = page_service.get_page_by_path(path)

        # Retrieve the revision by page id
        if page is not None:
            page_id = page.id

    if path is None:
        # Retrieve seo fields based on the module name.
        path = module_name

    return {'page': page, 'page_id': page_id,
            'activity': activity, 'activity_id': activity_id,
            'url': path}
