from flask_babel import lazy_gettext as _  # gettext
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, DateField
from wtforms.validators import InputRequired


class EditForm(Form):
    title = StringField(
        _('Title'), validators=[
            InputRequired(_('Title') + " " + _('required'))])
    date = DateField(
        _('Date'), validators=[
            InputRequired(_('Date') + " " + _('required'))],
        format='%Y-%m-%d')
    course = SelectField(_('Course'), coerce=int)
    education = SelectField(_('Education'), coerce=int)

    summary = FileField(_('Summary'))
