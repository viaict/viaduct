from viaduct import db
import datetime
from viaduct.models import BaseEntity


# many to many relationship tables
task_user = db.Table(
    'pimpy_task_user',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('pimpy_task.id')),
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
    deadline = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    line = db.Column(db.Integer)

    minute_id = db.Column(db.Integer, db.ForeignKey('pimpy_minute.id'))

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    group = db.relationship('Group', backref=db.backref('tasks',
                            lazy='dynamic'))

    users = db.relationship('User', secondary=task_user,
                            backref=db.backref('tasks', lazy='dynamic'),
                            lazy='dynamic')

    status = db.Column(db.Integer)

    status_meanings = [
        "Niet begonnen", "Begonnen", "Done",
        "Niet Done", "Gecheckt", "Verwijderd"]
    status_colors = [
        "btn-info", "btn-warning", "btn-success",
        "btn-danger", "btn-success", "btn-inverse"]

    def __init__(self, title, content, deadline, group_id, users,
                 minute_id, line, status):
        self.title = title
        self.content = content
        self.deadline = deadline
        self.group_id = group_id
        self.line = line
        self.users = users
        self.minute_id = minute_id
        self.status = status

    def get_task_id(self):
        return self.id

    def get_status_string(self):
        """
        Returns a string representing the status
        """
        if self.status >= 0 and self.status < len(self.status_meanings):
            return self.status_meanings[self.status]
        return "Onbekend"

    def update_status(self, status):
        if status >= 0 and status <= len(self.status_meanings):
            self.status = status
            db.session.commit()

    def get_status_color(self):
        """
        Returns a string representing the status
        """
        if self.status >= 0 and self.status < len(self.status_colors):
            return self.status_colors[self.status]
        return "Onbekend"

    @staticmethod
    def get_status_meanings():
        statusi = [0 for i in range(len(Task.status_meanings)-2)]
        for i in range(0, len(Task.status_meanings)-2):
            statusi[i] = [Task.status_meanings[i], Task.status_colors[i], i]
        return statusi

    def get_users(self):
        """
        Returns a list of users, comma separated
        """
        return ", ".join(map(lambda x: "%s %s" % (x.first_name, x.last_name),
                             self.users))


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

    tasks = db.relationship('Task', backref='minute', lazy='dynamic')

    def __init__(self, content, group_id, minute_date):
        self.content = content
        self.group_id = group_id
        self.minute_date = minute_date

    def get_name(self):
        """
        A representable (unique) name for minute
        """
        return 'minute%d' % self.id

    def get_timestamp(self):
        return self.timestamp

    def get_content(self):
        return self.content

    def get_content_numbered(self):
        s = ''
        for i, line in enumerate(self.content.split('\n')):
            s += '<a id="%dln%d" class="pimpy_minute_line"/>%s</a>' % \
                (self.id, i, line[:-1])
        return s

    def get_group(self):
        return self.group

    def get_minute_day(self):
        """ returns the date of when the meeting took place in yyyy-mm-dd"""
        return self.minute_date.strftime('%Y-%m-%d')

    def get_title(self):
        return "Van %s" % self.get_minute_day()
