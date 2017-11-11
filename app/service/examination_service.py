# from flask_babel import _

from app.repository import examination_repository
# from app.utils import file
from app.views.errors import ResourceNotFoundException


def find_examination_by_id(examination_id):
    return examination_repository.find_examination_by_id(examination_id)


def find_education_by_id(education_id):
    return examination_repository.find_education_by_id(education_id)


def find_course_by_id(course_id):
    return examination_repository.find_course_by_id(course_id)


def find_all_courses():
    return examination_repository.find_all_courses()


def find_all_educations():
    return examination_repository.find_all_educations()


def find_all_examinations_by_course(course_id):
    exams = examination_repository.find_all_examinations_by_course(course_id)
    if not exams:
        raise ResourceNotFoundException("Examination")
    return exams


def find_all_examinations_by_education(education_id):
    e = examination_repository.find_all_examinations_by_education(education_id)
    if not e:
        raise ResourceNotFoundException("Examination")
    return e


def create_examination(examination):
    examination_repository.create_examination(examination)


def create_education():
    pass


def create_course(course):
    examination_repository.create_course(course)


def update_examination(examination_id, exam_file, answer_file,
                       type, date, comment):
    pass


def update_education():
    pass


def update_course():
    pass


def delete_examination():
    pass


def delete_education(education_id):
    e = examination_repository.find_all_examinations_by_education(education_id)
    examination_repository.delete_examination(e)

    examination_repository.delete_education(education_id)


def delete_course(course_id):
    exams = examination_repository.find_all_examinations_by_course(course_id)
    examination_repository.delete_examination(exams)

    examination_repository.delete_course(course_id)
