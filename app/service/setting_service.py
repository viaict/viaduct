from app.repository import setting_repository
from app.views.errors import ResourceNotFoundException


def save_setting(setting):
    setting_repository.save(setting)


def get_setting_by_key(key):
    setting = setting_repository.find_by_key(key)
    if not setting:
        raise ResourceNotFoundException("setting", key)
    return setting


def delete_setting(setting):
    setting_repository.delete_setting(setting)
