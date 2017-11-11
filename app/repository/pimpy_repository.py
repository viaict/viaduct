from app import app, db
from app.models.group import Group
from app.models.pimpy import Minute, Task, TaskUserRel
from app.models.user import User

_date_format = app.config['DATE_FORMAT']


def find_minute_by_id(minute_id):
    return Minute.query.filter(Minute.id == minute_id).one_or_none()


def find_task_by_id(task_id):
    return Task.query.filter(Task.id == task_id).one_or_none()


def get_all_minutes_for_user(user):
    list_items = {}

    for group in user.groups:
        list_items[group.name] = Minute.query \
            .filter(Minute.group_id == group.id) \
            .order_by(Minute.minute_date.desc()) \
            .all()

    return list_items


def get_all_minutes_for_group(group_id, date_range=None):
    list_items = {}

    query = Minute.query.filter(Minute.group_id == group_id). \
        order_by(Minute.minute_date.desc())

    if date_range:
        query = query.filter(date_range[0] <= Minute.minute_date,
                             Minute.minute_date <= date_range[1])

    list_items[Group.query.filter(Group.id == group_id).first().name] \
        = query.all()

    return list_items


def get_all_tasks_for_groups(group_ids, date_range=None, user=None):
    query = TaskUserRel.query.join(Task).join(User)

    query = query.filter(Task.group_id.in_(group_ids))

    if user:
        query = query.filter(User.id == user.id)

    query = query.filter(~Task.status.in_((4, 5))).join(Group)

    if date_range:
        query = query.filter(date_range[0] <= Task.timestamp,
                             Task.timestamp <= date_range[1])

    return query.order_by(Group.name.asc(), User.first_name.asc(),
                          User.last_name.asc(), Task.id.asc())


def update_status(task, status):
    if 0 <= status <= len(Task.status_meanings):
        task.status = status
        db.session.commit()
        return True

    # TODO: raise exception
    return False


def add_task(task):
    db.session.add(task)
    db.session.commit()


def edit_task_title(task, title):
    task.title = title
    db.session.commit()


def edit_task_content(task, content):
    task.content = content
    db.session.commit()


def edit_task_users(task, users):
    task.users = users
    db.session.commit()
