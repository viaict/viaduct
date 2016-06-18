from flask.ext.wtf import Form
from wtforms import TextAreaField
from flask.ext.babel import lazy_gettext as _


class SeoForm(Form):
    nl_description = TextAreaField(
        _('Dutch description (max. 180 characters)'))
    en_description = TextAreaField(
        _('English description (max. 180 characters)'))
    nl_title = TextAreaField(_('Dutch title'))
    en_title = TextAreaField(_('English title'))
    nl_tags = TextAreaField(_('Dutch tags (comma seperated)'))
    en_tags = TextAreaField(_('English tags (comma seperated)'))
