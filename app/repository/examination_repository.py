# from sqlalchemy.orm import joinedload, raiseload

from app import db
# from app.models.activity import Activity
from app.models.course import Course
from app.models.education import Education
from app.models.examination import Examination


def find_examination_by_id(examination_id):
    pass


def find_education_by_id(education_id):
    pass


def find_course_by_id(course_id):
    return db.session.query(Course) \
        .filter_by(id=course_id) \
        .one_or_none()


def find_course_by_name(course_name):
    return db.session.query(Course) \
        .filter_by(name=course_name) \
        .one_or_none()


def find_all_courses():
    return db.session.query(Course) \
        .order_by(Course.name) \
        .all()


def find_all_educations():
    return db.session.query(Education) \
        .order_by(Education.name) \
        .all()


def find_all_examinations_by_course(course_id):
    return db.session.query(Examination) \
        .filter_by(course_id=course_id) \
        .all()


def find_all_examinations_by_education(education_id):
    return db.session.query(Examination) \
        .filter_by(education_id=education_id) \
        .all()


def create_examination():
    return Examination()


def create_education():
    pass


def create_course():
    return Course()


def delete_examination():
    pass


def delete_education():
    pass


def delete_course(course_id):
    course = db.session.query(Course) \
        .filter_by(id=course_id).first()
    db.session.delete(course)
    db.session.commit()


def save_examination():
    pass


def save_education():
    pass


def save_course(course):
    db.session.add(course)
    db.session.commit()
