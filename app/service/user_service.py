import bcrypt

from app.exceptions import ResourceNotFoundException
from app.repository import user_repository


def set_password(user_id, password):
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    user = get_user_by_id(user_id)
    user.password = password
    user_repository.save(user)
    return user


def get_user_by_email(email):
    user = user_repository.find_user_by_email(email)
    if not user:
        raise ResourceNotFoundException("user", email)
    return user


def get_user_by_id(user_id):
    user = find_by_id(user_id)
    if not user:
        raise ResourceNotFoundException('user', user_id)
    return user


def find_by_id(user_id):
    return user_repository.find_by_id(user_id)


def find_members():
    return user_repository.find_members()
