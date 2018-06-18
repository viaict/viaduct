from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Roles(Enum):
    """
    Roles used to secure the application.

    Note: When updating the list of roles do not change the key of an role,
    without creating a proper migration.
    """

    ACTIVITY_WRITE = _("Create activities")
    ALV_WRITE = _("Create ALVs")
    CHALLENGE_WRITE = _("Change challenges")
    DOMJUDGE_ADMIN = _("Display administrative buttons to DOMjudge")
    ELECTIONS_WRITE = _("Change election properties")
    EXAMINATION_WRITE = _("Change the examinations")
    FILE_READ = _("Read files")
    FILE_WRITE = _("Upload files")
    GROUP_READ = _("View groups")
    GROUP_WRITE = _("Change group members")
    GROUP_PERMISSIONS = _("Change group permissions")
    MOLLIE_READ = _("View mollie transactions")
    NAVIGATION_WRITE = _("Change the navigation")
    REDIRECT_WRITE = _("Change the redirects")
    NEWS_WRITE = _("Create news articles")
    PAGE_WRITE = _("Create pages")
    PIMPY_READ = _("View Pimpy")
    PIMPY_WRITE = _("Upload minutes and tasks")
    SEO_WRITE = _("Change SEO properties")
    USER_READ = _("Read user properties")
    USER_WRITE = _("Change user properties")
    VACANCY_READ = _("View vacancy overview")
    VACANCY_WRITE = _("Change vacancies")
    FINANCIAL_ADMIN = _("Manage financing related tasks")

    @classmethod
    def choices(cls):
        return [(choice, "%s" % choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls[item] if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.name)
