from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import TextAreaField

from app.forms.util import FieldTab, FieldTabGroup


class SeoForm(FlaskForm):
    nl_title = TextAreaField(_('Dutch title'))
    en_title = TextAreaField(_('English title'))
    nl_description = TextAreaField(
        _('Dutch description (max. 180 characters)'))
    en_description = TextAreaField(
        _('English description (max. 180 characters)'))
    nl_tags = TextAreaField(_('Dutch tags (comma seperated)'))
    en_tags = TextAreaField(_('English tags (comma seperated)'))

    details = FieldTabGroup([
        FieldTab(_('Dutch details'),
                 ['nl_title', 'nl_description', 'nl_tags']),
        FieldTab(_('English details'),
                 ['en_title', 'en_description', 'en_tags'])
    ])
