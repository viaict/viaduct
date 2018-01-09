from app import db
from app.models.pimpy import Task


def find_task_by_name_content_group(name, content, group):
    return db.query(Task).filter(
        Task.title == name,
        Task.content == content,
        Task.group_id == group.id).first()
