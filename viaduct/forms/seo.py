from flask.ext.wtf import Form
from wtforms import TextAreaField
from flask.ext.babel import lazy_gettext as _

class SeoForm(Form):
    nl_description = TextAreaField(_('Nederlandse beschrijving (max. 180 karakters)'))
    en_description = TextAreaField(_('English description (max. 180 characters)'))
    nl_title = TextAreaField(_('Nederlanse titel'))
    en_title = TextAreaField(_('English title'))
    nl_tags = TextAreaField(_('Nederlandse tags (komma seperated)'))
    en_tags = TextAreaField(_('English tags (comma seperated)'))

