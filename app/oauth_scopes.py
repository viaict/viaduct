from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Scopes(Enum):
    pimpy_read = _("Read access to your Pimpy data")
    pimpy_write = _("Write access to your Pimpy data")
