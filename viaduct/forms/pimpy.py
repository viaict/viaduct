from flask_wtf import Form
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, \
    SelectField, BooleanField
from wtforms.validators import InputRequired, Optional

import datetime

from viaduct.models.pimpy import Task
from viaduct.models import Group
from viaduct import application


DATE_FORMAT = application.config['DATE_FORMAT']



class AddTaskShortForm(Form):
    """ Form to show when you are viewing a task for group """
    name = StringField('Name', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    deadline = DateTimeField('Deadline', format=DATE_FORMAT,
                             default=datetime.date.today())

    minute_id = IntegerField(
        'Minute ID', default=-1,
        description='Fill in -1 if this is unknown or impossible.')

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


    def __init__(self, formdata=None, obj=None, prefix='', group_id='all', **kwargs):
        # group and line are no options to set with the form

        # do we check valid stuff like this? Probably not
        if group_id == 'all':
            raise Exception('Invalid group id for AddTaskShortForm :(');

        self.group = group_id
        self.line = -1

        Form.__init__(self, formdata, obj, prefix, **kwargs)




class AddTaskForm(AddTaskShortForm):
    """ Form to show when you add a new task through the side bar menu"""

    # timestamp
    line = IntegerField(
        'Line', default=-1,
        description='Fill in -1 if this is unknown or impossible.')
    group = SelectField('Group')


    def load_groups(self, groups):
        self.group.choices = map(lambda x: (x.id, x.name), groups)

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        Form.__init__(self, formdata, obj, prefix, **kwargs)


class EditTaskForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[Optional()])
    deadline = DateTimeField('Deadline',
                             format=DATE_FORMAT, default=datetime.date.today())
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
    date = DateTimeField('Deadline', format=DATE_FORMAT,
                         default=datetime.date.today())
    parse_tasks = BooleanField('Parse', default=True)

    def load_groups(self, groups, default=-1):
        self.group.choices = map(lambda x: (x.id, x.name), groups)
        self.group.default = default

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        kwargs.setdefault('group', kwargs.get('default', -1))

        Form.__init__(self, formdata, obj, prefix, **kwargs)
