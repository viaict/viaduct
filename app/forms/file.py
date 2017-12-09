from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from flask_babel import lazy_gettext as _


class FileForm(FlaskForm):
    file = FileField(_('File'), render_kw={'multiple': True})
