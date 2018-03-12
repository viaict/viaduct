import datetime

from flask_babel import _
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, \
    BooleanField
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
        query_factory=lambda: group_service.get_group_for_user(current_user),
        get_label=lambda x: x.name)
    users = StringField(_('Users'))
    status = SelectField(_('Status'), coerce=int,
                         choices=pimpy_service.get_task_status_choices())


class AddMinuteForm(FlaskForm):
    # TODO: should try and resize stuff, especially the content field
    content = TextAreaField('Content', validators=[InputRequired()])
    group = SelectField('Group', validators=[InputRequired()])
    # FIXME: datetime is now printed badly in the actual form!!! :( :(
    date = DateTimeField('Date', format=DATE_FORMAT,
                         default=datetime.date.today)
    parse_tasks = BooleanField('Parse', default=True)

    def load_groups(self, groups, default=-1):
        self.group.choices = map(lambda x: (x.id, x.name), groups)
        self.group.default = default

    def __init__(self, formdata=None, *args, **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        FlaskForm.__init__(self, formdata, *args, **kwargs)
