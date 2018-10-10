from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Scopes(Enum):
    pimpy = _("Access to pimpy")
    user = _("Access to users")
    group = _("Access to groups")
    examination = _("Access to examinations")

    @classmethod
    def choices(cls):
        return [(choice, "%s: %s" % (choice.name, choice.value))
                for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls[item] if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.name)
