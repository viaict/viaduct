from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import InputRequired
from flask.ext.babel import lazy_gettext as _


class NavigationEntryForm(Form):
    nl_title = StringField(_('Dutch title'), validators=[
        InputRequired(_('Dutch title') + " " + ('is required'))
    ])
    en_title = StringField(_('English title'), validators=[
        InputRequired(_('English title') + ' ' + ('is required'))
    ])
    url = StringField('URL', validators=[
        InputRequired('URL ' + _('is required'))
    ])
    parent_id = StringField(_('List'))
    external = BooleanField(_('External link'), default=False)
    activity_list = BooleanField(_('List of activities'), default=False)
