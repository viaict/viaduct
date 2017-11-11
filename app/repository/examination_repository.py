# from sqlalchemy.orm import joinedload, raiseload

from app import db
# from app.models.activity import Activity
from app.models.course import Course
from app.models.education import Education


def find_examination_by_id(examination_id):
    pass


def find_education_by_id():
    pass


def find_course_by_id():
    pass


def find_all_courses():
    return db.session.query(Course) \
        .order_by(Course.name) \
        .all()


def find_all_educations():
    return db.session.query(Education) \
        .order_by(Education.name) \
        .all()


def find_all_examinations_by_course():
    pass


def find_all_examinations_by_education():
    pass


def create_examination(examination):
    db.session.add(examination)
    db.session.commit()


def create_education():
    pass


def create_course(course):
    db.session.add(course)
    db.session.commit()


def delete_examination():
    pass


def delete_education():
    pass


def delete_course():
    pass


def save_examination():
    pass


def save_education():
    pass


def save_course():
    pass
