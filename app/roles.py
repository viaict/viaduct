from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Roles(Enum):
    """
    Roles used to secure the application.

    Note: When updating the list of roles do not change the key of an role,
    without creating a proper migration.
    """
    ACTIVITY_WRITE = _("Edit activities")
    ALV_WRITE = _("Edit ALVs")
    CHALLENGE_WRITE = _("Edit challenges")
    DOMJUDGE_ADMIN = _("DOMjudge administrator")
    ELECTIONS_WRITE = _("Edit elections")
    EXAMINATION_WRITE = _("Edit examinations")
    FILE_READ = _("Read files")
    FILE_WRITE = _("Edit files")
    GROUP_READ = _("Read groups")
    GROUP_WRITE = _("Edit groups")
    GROUP_PERMISSIONS = _("Edit group permissions")
    MOLLIE_READ = _("Read mollie payments")
    NAVIGATION_WRITE = _("Edit navigation and redirect")
    NEWS_WRITE = _("Edit news")
    PAGE_WRITE = _("Edit pages")
    PIMPY_READ = _("Read Pimpy")
    PIMPY_WRITE = _("Edit Pimpy")
    SEO_WRITE = _("Edit search-engine optimizations")
    USER_READ = _("Read user")
    USER_WRITE = _("Edit user")
    VACANCY_READ = _("Read vacancy")
    VACANCY_WRITE = _("Edit vacancy")

    @classmethod
    def choices(cls):
        return [(choice, "%s" % choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls[item] if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.name)
