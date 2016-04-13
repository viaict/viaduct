# coding: utf-8

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired
from flask.ext.babel import lazy_gettext as _  # gettext


class CourseForm(Form):
    title = StringField(_('Title'), validators=[InputRequired(
        message=_('No title given.'))])
    description = StringField(_('Description'))


class EducationForm(Form):
    title = StringField(_('Title'), validators=[InputRequired(
        message=_('No title given.'))])
