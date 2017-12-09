from app import app
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, DateField
from wtforms.validators import InputRequired, Optional

from app.models.examination import test_type_default


class CourseForm(FlaskForm):
    title = StringField(_('Title'), validators=[InputRequired(
        message=_('No title given.'))])
    description = StringField(_('Description'))


class EducationForm(FlaskForm):
    title = StringField(_('Title'), validators=[InputRequired(
        message=_('No title given.'))])


class EditForm(FlaskForm):
    date = DateField(_('Date'),
                     validators=[Optional()],
                     format=app.config['DATE_FORMAT'])
    course = SelectField(_('Course'), coerce=int,
                         validators=[InputRequired(
                             message=_('No course given'))])
    education = SelectField(_('Education'), coerce=int,
                            validators=[InputRequired(
                                message=_('No education given'))])
    test_type = SelectField(_('Examination type'), coerce=str,
                            default=test_type_default,
                            validators=[InputRequired(
                                message=_('No examination kind given'))])
    comment = StringField(_('Comment'))
    examination = FileField(_('Examination'))
    answers = FileField(_('Answers'))
