from flask_sqlalchemy import Pagination
from sqlalchemy import or_

from app import db
from app.models.course import Course
from app.models.education import Education
from app.models.examination import Examination


def find_examination_by_id(exam_id):
    return db.session.query(Examination)\
        .filter_by(id=exam_id)\
        .one_or_none()


def find_education_by_id(education_id):
    return db.session.query(Education)\
        .filter_by(id=education_id)\
        .one_or_none()


def find_course_by_id(course_id):
    return db.session.query(Course)\
        .filter_by(id=course_id)\
        .one_or_none()


def find_education_by_name(name):
    return db.session.query(Education)\
        .filter_by(name=name)\
        .one_or_none()


def find_course_by_name(name):
    return db.session.query(Course)\
        .filter_by(name=name)\
        .one_or_none()


def find_all_courses():
    return db.session.query(Course)\
        .order_by(Course.name)\
        .all()


def paginated_search_all_courses(page: int, page_size: int = 15,
                                 search: str = "") -> Pagination:
    q = db.session.query(Course) \
        .order_by(Course.name.asc())
    if search is not "":
        q = q.filter(or_(Course.name.ilike(f"%{search}%"),
                         Course.description.ilike(f"%{search}%")))
    return q.paginate(page, page_size, False)


def find_all_educations():
    return db.session.query(Education)\
        .order_by(Education.name)\
        .all()


def paginated_search_all_educations(page: int, page_size: int = 15,
                                    search: str = "") -> Pagination:
    q = db.session.query(Education) \
        .order_by(Education.name.asc())
    if search is not "":
        q = q.filter(or_(Education.name.ilike(f"%{search}%")))
    return q.paginate(page, page_size, False)


def find_all_examinations(page_nr=1, per_page=15):
    return db.session.query(Examination)\
        .join(Course)\
        .order_by(Course.name)\
        .order_by(Examination.date.desc())\
        .paginate(page_nr, per_page)


def find_all_examinations_by_course(course_id):
    return db.session.query(Examination)\
        .filter_by(course_id=course_id)\
        .all()


def find_all_examinations_by_education(education_id):
    return db.session.query(Examination)\
        .filter_by(education_id=education_id)\
        .all()


def search_examinations_by_courses(courses, page_nr=1, per_page=15):
    return db.session.query(Examination)\
        .join(Course)\
        .filter(Course.id.in_(courses))\
        .order_by(Examination.date.desc())\
        .paginate(page_nr, per_page, True)


def create_examination():
    return Examination()


def create_education():
    return Education()


def create_course():
    return Course()


def delete_examination(examination_id):
    exam = db.session.query(Examination)\
        .filter_by(id=examination_id).first()
    db.session.delete(exam)
    db.session.commit()


def delete_education(education_id):
    education = db.session.query(Education)\
        .filter_by(id=education_id).first()
    db.session.delete(education)
    db.session.commit()


def delete_course(course: Course):
    db.session.delete(course)
    db.session.commit()


def save_examination(exam):
    db.session.add(exam)
    db.session.commit()


def save_education(education):
    db.session.add(education)
    db.session.commit()


def save_course(course):
    db.session.add(course)
    db.session.commit()
