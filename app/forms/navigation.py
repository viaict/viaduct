from flask_wtf import Form
from flask_babel import lazy_gettext as _
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import InputRequired, ValidationError


class NavigationEntryForm(Form):
    nl_title = StringField(_('Dutch title'), validators=[
        InputRequired(_('Dutch title') + " " + ('is required'))
    ])
    en_title = StringField(_('English title'), validators=[
        InputRequired(_('English title') + ' ' + ('is required'))
    ])
    url = StringField('URL')
    page_id = SelectField(_('Page'), coerce=int)
    # parent_id = StringField(_('List'))
    external = BooleanField(_('External link'), default=False)
    activity_list = BooleanField(_('List of activities'), default=False)

    def validate_url(self, field):
        if self.page_id.data == -1 and not field.data.strip():
            raise ValidationError('URL ' + _('is required'))
