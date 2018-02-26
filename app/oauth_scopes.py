from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Scopes(Enum):
    pimpy_read = _("Read access to your Pimpy data")
    pimpy_write = _("Write access to your Pimpy data")

    @classmethod
    def choices(cls):
        return [(choice, "%s: %s" % (choice.name, choice.value))
                for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls[item] if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.name)
