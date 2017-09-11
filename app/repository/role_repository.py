from app import db
from app.models.group import Group
from app.models.role_model import GroupRole
from app.models.user import User


def load_user_roles(user_id):
    return db.session.query(GroupRole.role).join(GroupRole.group, Group.users)\
        .filter(User.id == user_id).group_by(GroupRole.role).all()
