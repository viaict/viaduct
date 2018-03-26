import datetime

from flask_babel import _
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Optional

from app import app
from app.service import group_service, pimpy_service

DATE_FORMAT = app.config['DATE_FORMAT']


class AddTaskForm(FlaskForm):
    name = StringField(_('Name'), validators=[InputRequired()])
    content = TextAreaField(_('Content'), validators=[Optional()])
    group = QuerySelectField(
        _('Group'),
        query_factory=lambda: group_service.get_groups_for_user(current_user),
        get_label=lambda x: x.name)
    users = StringField(_('Users'))
    status = SelectField(_('Status'), coerce=int,
                         choices=pimpy_service.get_task_status_choices())


class AddMinuteForm(FlaskForm):
    content = TextAreaField(_('Minute content'), validators=[InputRequired()])
    group = QuerySelectField(
        _('Group'),
        query_factory=lambda: group_service.get_groups_for_user(current_user),
        get_label=lambda x: x.name)

    date = DateTimeField(_('Date'), format=DATE_FORMAT,
                         default=datetime.date.today)
