from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import SubmitField

from flask_babel import lazy_gettext as _


class FileForm(Form):
    file = FileField(_('File'))
    submit = SubmitField(_('Upload'))
