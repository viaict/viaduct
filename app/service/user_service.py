from app.repository import user_repository


def find_by_id(user_id):
    return user_repository.find_by_id(user_id)


def find_members():
    return user_repository.find_members()
