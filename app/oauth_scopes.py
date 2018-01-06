from enum import Enum, unique

from flask_babel import lazy_gettext as _


@unique
class Scopes(Enum):
    PIMPY = _("Access to your Pimpy data")
