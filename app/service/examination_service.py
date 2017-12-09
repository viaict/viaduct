from app.repository import examination_repository
from app.exceptions import ResourceNotFoundException, BusinessRuleException, \
    DuplicateResourceException


def get_examination_by_id(examination_id):
    return examination_repository.find_examination_by_id(examination_id)


def get_education_by_id(education_id):
    education = examination_repository.find_education_by_id(education_id)
    if not education:
        raise ResourceNotFoundException("Education", education_id)
    return education


def get_course_by_id(course_id):
    course = examination_repository.find_course_by_id(course_id)
    if not course:
        raise ResourceNotFoundException("Course", course_id)
    return course


def find_all_courses():
    return examination_repository.find_all_courses()


def find_all_educations():
    return examination_repository.find_all_educations()


def find_all_examinations_by_course(course_id):
    get_course_by_id(course_id)
    return examination_repository.find_all_examinations_by_course(course_id)


def find_all_examinations_by_education(education_id):
    get_education_by_id(education_id)
    return examination_repository.\
        find_all_examinations_by_education(education_id)


def add_course(name, description):
    existing_course = examination_repository.find_course_by_name(name)
    if existing_course:
        raise DuplicateResourceException(name, existing_course.id)

    course = examination_repository.create_course()
    course.name = name
    course.description = description

    examination_repository.save_course(course)


def add_education(name):
    existing_education = examination_repository.find_education_by_name(name)
    if existing_education:
        raise DuplicateResourceException(name, existing_education.id)

    education = examination_repository.create_education()
    education.name = name

    examination_repository.save_education(education)


def create_education(exam):
    examination_repository.create_education(exam)
    pass


def create_course(course):
    examination_repository.create_course(course)


def update_examination(examination_id, exam_file, answer_file,
                       type, date, comment):
    pass


def update_education(education_id, name):
    education = examination_repository.find_education_by_id(education_id)
    if education.name != name and \
            examination_repository.find_course_by_name(name):
        raise DuplicateResourceException("Education", name)
    education.name = name

    examination_repository.save_education(education)


def update_course(course_id, name, description):
    course = examination_repository.find_course_by_id(course_id)
    if course.name != name and \
            examination_repository.find_course_by_name(name):
        raise DuplicateResourceException("Course", name)
    course.name = name
    course.description = description

    examination_repository.save_course(course)


def delete_examination():
    pass


def count_examinations_by_course(course_id):
    exams = examination_repository.find_all_examinations_by_course(course_id)
    return len(exams)


def count_examinations_by_education(education_id):
    exams = examination_repository.\
        find_all_examinations_by_education(education_id)
    return len(exams)


def delete_education(education_id):
    if count_examinations_by_education(education_id) >= 1:
        raise BusinessRuleException("Education has examinations")
    else:
        examination_repository.delete_education(education_id)


def delete_course(course_id):
    if count_examinations_by_course(course_id) >= 1:
        raise BusinessRuleException("Course has examinations")
    else:
        examination_repository.delete_course(course_id)
