from flask_wtf import Form
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, \
    SelectField, BooleanField
from wtforms.validators import InputRequired, Optional

import datetime

from viaduct.models.pimpy import Task
from viaduct import application


DATE_FORMAT = application.config['DATE_FORMAT']


class AddTaskForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    # timestamp
    line = IntegerField(
        'Line', default=-1,
        description='Fill in -1 if this is unknown or impossible.')

    minute_id = IntegerField(
        'Minute ID', default=-1,
        description='Fill in -1 if this is unknown or impossible.')

    group = SelectField('Group')
    users = TextAreaField(
        'Users',
        description='Type comma separated names for whom this task is, in a '
                    'similar manner as you are familiar with whilst taking '
                    'minutes.',
        validators=[InputRequired()])

    status = SelectField(
        'Status',
        choices=map(lambda x, y: (x, y),
                    range(0, len(Task.status_meanings)),
                    Task.status_meanings), validators=[])

    def load_groups(self, groups):
        self.group.choices = map(lambda x: (x.id, x.name), groups)

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        Form.__init__(self, formdata, obj, prefix, **kwargs)


class EditTaskForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    # timestamp
    line = IntegerField('Line', default=-1,
                        description='Fill in -1 if this is '
                                    'unknown or impossible.')
    minute_id = IntegerField('Minute ID', default=-1,
                             description='Fill in -1 if this is unknown or '
                                         'impossible.')
    group = SelectField('Group')
    users = TextAreaField('Users',
                          description='Type comma separated names for whom '
                                      'this task is, in a similar manner as '
                                      'you are familiar with whilst taking '
                                      'minutes.', validators=[InputRequired()])

    def load_groups(self, groups, default=-1):
        self.group.choices = map(lambda x: (x.id, x.name), groups)
        self.group.default = default

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        Form.__init__(self, formdata, obj, prefix, **kwargs)


class AddMinuteForm(Form):
    # TODO: should try and resize stuff, especially the content field
    content = TextAreaField('Content', validators=[InputRequired()])
    group = SelectField('Group', validators=[InputRequired()])
    # FIXME: datetime is now printed badly in the actual form!!! :( :(
    date = DateTimeField('Date', format=DATE_FORMAT,
                         default=datetime.date.today())
    parse_tasks = BooleanField('Parse', default=True)

    def load_groups(self, groups, default=-1):
        self.group.choices = map(lambda x: (x.id, x.name), groups)
        self.group.default = default

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        Form.__init__(self, formdata, obj, prefix, **kwargs)
