from app import db
from app.models.setting_model import Setting


def create_setting():
    return Setting()


def save(setting):
    db.session.add(setting)
    db.session.commit()
    return setting


def find_by_key(key):
    return db.session.query(Setting).filter_by(key=key).first()


def delete_setting(setting):
    db.session.delete(setting)
    db.session.commit()
