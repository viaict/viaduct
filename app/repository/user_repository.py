from sqlalchemy.orm import raiseload

from app import db
from app.models.user import User


def find_members():
    return db.session.query(User) \
        .filter_by(has_paid=True) \
        .order_by(User.first_name) \
        .options(raiseload('*')).all()


def find_by_id(user_id):
    return db.session.query(User).filter_by(id=user_id).one_or_none()
