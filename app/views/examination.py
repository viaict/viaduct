from flask import Blueprint
from flask import flash, session, redirect, render_template, request, url_for
from flask import abort
from flask_babel import gettext as _
from flask_login import current_user
from fuzzywuzzy import fuzz

from app.decorators import require_role, require_membership
from app.forms import init_form
from app.forms.examination import EditForm
from app.models.examination import test_types
from app.roles import Roles
from app.service import role_service, examination_service, file_service
from app.enums import FileCategory

blueprint = Blueprint('examination', __name__, url_prefix='/examination')


@blueprint.route('/view/<int:exam_id>/<any(exam,answers):doc_type>/',
                 methods=['GET'])
@require_membership
def view(exam_id, doc_type):
    exam = examination_service.get_examination_by_id(exam_id)

    if doc_type == 'exam':
        _file = exam.examination_file
        fn = exam.examination_filename
    elif doc_type == 'answers' and exam.answers_file is not None:
        _file = exam.answers_file
        fn = exam.answers_filename
    else:
        return abort(404)

    content = file_service.get_file_content(_file)
    headers = file_service.get_file_content_headers(_file, display_name=fn)

    return content, headers


@blueprint.route('/add/', methods=['GET', 'POST'])
@require_membership
@require_role(Roles.EXAMINATION_WRITE)
def add():
    form = EditForm(request.form)

    courses = examination_service.find_all_courses()
    educations = examination_service.find_all_educations()

    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    form.test_type.choices = test_types.items()

    if form.validate_on_submit():
        exam_file_data = request.files.get('examination', None)
        answer_file_data = request.files.get('answers', None)

        # Exam file is required
        if len(exam_file_data.name) > 0:
            exam_file = file_service.add_file(FileCategory.EXAMINATION,
                                              exam_file_data,
                                              exam_file_data.filename)
        else:
            flash(_('No examination uploaded.'), 'danger')
            return render_template('examination/edit.htm',
                                   courses=courses,
                                   educations=educations,
                                   form=form,
                                   test_types=test_types, new_exam=True)

        # Answer file is optional
        if len(answer_file_data.name) > 0:
            answers_file = file_service.add_file(FileCategory.EXAMINATION,
                                                 answer_file_data,
                                                 answer_file_data.filename)
        else:
            answers_file = None
            flash(_('No answers uploaded.'), 'warning')

        examination_service.add_examination(
            exam_file, form.date.data,
            form.comment.data, form.course.data,
            form.education.data, form.test_type.data,
            answers_file)

        flash(_('Examination successfully uploaded.'), 'success')
        return redirect(url_for('examination.view_examination'))

    return render_template('examination/edit.htm',
                           courses=courses,
                           educations=educations,
                           form=form,
                           test_types=test_types, new_exam=True)


@blueprint.route('/edit/<int:exam_id>/', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def edit(exam_id):
    exam = examination_service.get_examination_by_id(exam_id)

    session['examination_edit_id'] = exam_id

    form = init_form(EditForm, obj=exam)

    courses = examination_service.find_all_courses()
    educations = examination_service.find_all_educations()

    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    form.test_type.choices = test_types.items()

    if form.validate_on_submit():
        exam_file_data = request.files.get('examination', None)
        answer_file_data = request.files.get('answers', None)

        old_examination_file = None
        old_answers_file = None

        if exam_file_data is not None:
            exam_file = file_service.add_file(FileCategory.EXAMINATION,
                                              exam_file_data,
                                              exam_file_data.filename)
            old_examination_file = exam.examination_file
        else:
            exam_file = exam.examination_file
            flash(_('No examination uploaded.'), 'warning')

        if answer_file_data is not None:
            answers_file = file_service.add_file(FileCategory.EXAMINATION,
                                                 answer_file_data,
                                                 answer_file_data.filename)
            old_answers_file = exam.answers_file
        else:
            answers_file = exam.answers_file
            flash(_('No answers uploaded.'), 'warning')

        date = form.date.data
        comment = form.comment.data
        course_id = form.course.data
        education_id = form.education.data
        test_type = form.test_type.data

        examination_service.update_examination(exam_id, exam_file, date,
                                               comment, course_id,
                                               education_id, test_type,
                                               answers_file)

        if old_examination_file is not None:
            file_service.delete_file(old_examination_file)

        if old_answers_file is not None:
            file_service.delete_file(old_answers_file)

        flash(_('Examination successfully changed.'), 'success')

        return redirect(url_for('examination.edit', exam_id=exam_id))
    else:
        # Load the existing field values
        form.course.data = exam.course_id
        form.education.data = exam.education_id
        form.test_type.data = exam.test_type
        form.comment.data = exam.comment

    return render_template('examination/edit.htm',
                           title=_('Examinations'),
                           form=form, examination=exam,
                           courses=courses, educations=educations,
                           new_exam=False)


@blueprint.route('/delete/<int:exam_id>/', methods=['POST'])
@require_role(Roles.EXAMINATION_WRITE)
def delete(exam_id):
    search = request.args.get('search', None)

    exam = examination_service.get_examination_by_id(exam_id)
    if exam is not None:
        examination_service.delete_examination(exam_id)
        file_service.delete_file(exam.examination_file)
        if exam.answers_file is not None:
            file_service.delete_file(exam.answers_file)

        flash(_('Examination successfully deleted.'), 'success')
    else:
        flash(_('Examination does not exist.'), 'danger')

    return redirect(url_for('.view_examination', search=search))


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def view_examination(page_nr=1):
    if request.args.get('search'):
        search = request.args.get('search')

        courses = examination_service.find_all_courses()
        course_scores = {}

        search_lower = search.lower().strip()

        # Search in all courses for matches in the course name
        for course in courses:
            course_score = fuzz. \
                partial_ratio(search_lower, course.name.lower())
            # If score is higher than a certain threshold, display in results
            if course_score > 75:
                course_scores[course.id] = course_score

        # Make a list of all course ids, sorted by their similarity score
        ranked_courses = sorted(course_scores,
                                key=course_scores.get, reverse=True)

        if len(ranked_courses) == 0:
            examinations = None
        else:

            # Query the exams. The filter part makes sure only the ranked
            # courses are returned. The order_by clause makes sure the exams
            # are first sorted by course according to the ranking and then
            # sorted by date of the exam
            examinations = examination_service \
                .search_examinations_by_courses(ranked_courses, page_nr, 15)
    else:
        search = ""
        # Query the exams. The order_by part makes sure the exams are sorted
        # by course and within a course are sorted by date
        examinations = examination_service\
            .find_all_examinations(page_nr, 15)

    can_write = role_service.user_has_role(current_user,
                                           Roles.EXAMINATION_WRITE)

    return render_template('examination/view.htm',
                           examinations=examinations, search=search,
                           title=_('Examinations'), test_types=test_types,
                           can_write=can_write)
