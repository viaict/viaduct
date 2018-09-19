import baas32 as b32
import datetime
from flask_babel import lazy_gettext as _
from jinja2 import escape

from app import db, constants
from app.models.base_model import BaseEntity

# many to many relationship tables
task_user = db.Table(
    'pimpy_task_user',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('task_id', db.Integer,
              db.ForeignKey('pimpy_task.id', ondelete='cascade')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class TaskUserRel(db.Model):
    __table__ = task_user

    task = db.relationship('Task')
    user = db.relationship('User')


class Task(db.Model, BaseEntity):
    __tablename__ = 'pimpy_task'

    prints = ('id', 'title')

    title = db.Column(db.Text)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    line = db.Column(db.Integer)

    minute_id = db.Column(db.Integer,
                          db.ForeignKey('pimpy_minute.id', ondelete='cascade'))
    minute = db.relationship('Minute',
                             backref=db.backref('tasks', lazy='dynamic'))

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group',
                            backref=db.backref('tasks', lazy='dynamic'))

    users = db.relationship('User', secondary=task_user,
                            backref=db.backref('tasks', lazy='dynamic'),
                            lazy='dynamic')

    status = db.Column(db.Integer)

    status_meanings = [
        _("Not started"), _("Started"), _("Done"),
        _("Not Done"), _("Checked"), _("Deleted")]

    # TODO: no view related code here
    status_colors = [
        "btn-info", "btn-warning", "btn-success",
        "btn-danger", "btn-success", "btn-inverse"]

    @property
    def b32_id(self):
        return b32.encode(self.id)

    def get_status_string(self):
        """Return a string representing the status."""
        if 0 <= self.status < len(self.status_meanings):
            return self.status_meanings[self.status]
        return _("Unknown")

    def get_status_color(self):
        """Return a string representing the status."""
        if 0 <= self.status < len(self.status_colors):
            return self.status_colors[self.status]
        return "Onbekend"

    @staticmethod
    def get_status_meanings():
        statusi = [0 for _ in range(len(Task.status_meanings) - 2)]
        for i in range(0, len(Task.status_meanings) - 2):
            statusi[i] = [Task.status_meanings[i], Task.status_colors[i], i]
        return statusi

    # TODO: view code
    def get_users(self, include_break_spans=False):
        """
        Return a list of users, comma separated.

        The usernames are escaped, so the resulting string is safe to render.
        When include_break_spans is set to True, each name is
        wrapped inside a span which does not allow breaking, so webbrowsers
        will only break on full names.
        """

        users = map(
            lambda x: str(escape("%s %s" % (x.first_name, x.last_name))),
            self.users)

        if include_break_spans:
            users = map(lambda x: "<span style='white-space: nowrap'>" +
                                  x + "</span>", users)
        return ", ".join(users)


class Minute(db.Model, BaseEntity):
    __tablename__ = 'pimpy_minute'

    # timestamp when the minutes were uploaded
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    content = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', backref=db.backref('minutes',
                                                        lazy='dynamic'))

    # the date when the meeting took place
    minute_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def get_name(self):
        """Representable (unique) name for minute."""
        return 'minute%d' % self.id

    def get_content_lines(self):
        for i, line in enumerate(self.content.split('\n')):
            yield (self.id, i, line[:-1])

    def get_minute_day(self):
        """Return the date of when the meeting took place in ryyy-mm-dd."""
        return self.minute_date.strftime(constants.DATE_FORMAT)

    def get_title(self):
        return _("From %(day)s", day=self.get_minute_day())
