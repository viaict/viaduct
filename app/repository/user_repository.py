from sqlalchemy.orm import raiseload

from app import db
from app.models.user import User


def create_user():
    user = User('_')
    user.email = None
    return user


def save(user):
    db.session.add(user)
    db.session.commit()


def save_all(users):
    db.session.add_all(users)
    db.session.commit()


def find_members():
    return db.session.query(User) \
        .filter_by(has_paid=True) \
        .order_by(User.first_name) \
        .options(raiseload('*')).all()


def find_by_id(user_id):
    return db.session.query(User).filter_by(id=user_id).one_or_none()


def find_user_by_email(email):
    return db.session.query(User).filter_by(email=email).one_or_none()


def find_user_by_student_id(student_id):
    return db.session.query(User) \
        .filter_by(student_id=student_id,
                   student_id_confirmed=True) \
        .one_or_none()


def find_all_users_with_unconfirmed_student_id(student_id):
    return db.session.query(User) \
        .filter_by(student_id=student_id,
                   student_id_confirmed=False) \
        .all()
