from flask_login import current_user

from app import app
from app.repository import role_repository


def user_has_role(user, role):
    return role.value in user.roles


@app.before_request
def load_user_roles():
    current_user.roles = [role.role for role in
                          role_repository.load_user_roles(current_user.id)]
