from app import app, db
from app.enums import PimpyTaskStatus
from app.exceptions import BusinessRuleException
from app.models.group import Group
from app.models.pimpy import Minute, Task, TaskUserRel
from app.models.user import User

_date_format = app.config['DATE_FORMAT']


def find_minute_by_id(minute_id):
    return db.session.query(Minute).filter(Minute.id == minute_id) \
        .one_or_none()


def find_task_by_id(task_id):
    return db.session.query(Task).filter(Task.id == task_id).one_or_none()


def get_all_minutes_for_user(user):
    res = []

    for group in user.groups:
        minutes = db.session.query(Minute) \
            .filter(Minute.group_id == group.id) \
            .order_by(Minute.minute_date.desc()) \
            .all()

        res.append({
            'group_name': group.name,
            'minutes': minutes
        })

    return res


def get_all_minutes_for_group(group, date_range=None):
    res = []

    query = db.session.query(Minute).filter(Minute.group == group). \
        order_by(Minute.minute_date.desc())

    if date_range:
        query = query.filter(date_range[0] <= Minute.minute_date,
                             Minute.minute_date <= date_range[1])

    res.append({
        'group_name': group.name,
        'minutes': query.all()
    })

    return res


def get_all_tasks_for_user(user, date_range=None):
    query = db.session.query(TaskUserRel) \
        .join(Task).join(User) \
        .filter(TaskUserRel.user == user) \
        .filter(~Task.status.in_((PimpyTaskStatus.CHECKED.value,
                                  PimpyTaskStatus.DELETED.value)))

    if date_range:
        query = query.filter(date_range[0] <= Task.timestamp,
                             Task.timestamp <= date_range[1])

    query = query.order_by(
        User.first_name.asc(), User.last_name.asc(), Task.id.asc()
    )

    return query.all()


def get_all_tasks_for_group(group, date_range=None, user=None):
    query = db.session.query(TaskUserRel) \
        .join(Task).join(User).join(Group) \
        .filter(Task.group == group) \
        .filter(~Task.status.in_((PimpyTaskStatus.CHECKED.value,
                                  PimpyTaskStatus.DELETED.value)))

    if date_range:
        query = query.filter(date_range[0] <= Task.timestamp,
                             Task.timestamp <= date_range[1])

    if user:
        query = query.filter(User.id == user.id)

    query = query.order_by(
        Group.name.asc(),
        User.first_name.asc(), User.last_name.asc(), Task.id.asc()
    )

    return query.all()


def get_all_tasks_for_users_in_groups(groups, date_range=None):
    query = db.session.query(TaskUserRel) \
        .join(Task).join(User).join(Group) \
        .filter(Task.group_id.in_([g.id for g in groups])) \
        .filter(~Task.status.in_((PimpyTaskStatus.CHECKED.value,
                                  PimpyTaskStatus.DELETED.value)))

    if date_range:
        query = query.filter(date_range[0] <= Task.timestamp,
                             Task.timestamp <= date_range[1])
    query = query.order_by(
        Group.name.asc(),
        User.first_name.asc(), User.last_name.asc(), Task.id.asc()
    )
    return query.all()


def update_status(task, status):
    if not 0 <= status <= len(Task.status_meanings):
        raise BusinessRuleException('Invalid status')

    task.status = status
    db.session.commit()


def add_task(title, content, group, users, minute, line, status):
    task = Task()
    task.title = title
    task.content = content
    task.group = group
    task.users = users
    task.minute = minute
    task.line = line
    task.status = status
    db.session.add(task)
    db.session.commit()
    return task


def edit_task_title(task, title):
    task.title = title
    db.session.commit()


def edit_task_content(task, content):
    task.content = content
    db.session.commit()


def edit_task_users(task, users):
    task.users = users
    db.session.commit()


def add_minute(content, date, group):
    minute = Minute()
    minute.content = content
    minute.group = group
    minute.minute_date = date
    db.session.add(minute)
    db.session.commit()
    return minute
