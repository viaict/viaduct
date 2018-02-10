import os

from flask import Blueprint
from flask import flash, session, redirect, render_template, request, url_for
from flask_babel import gettext as _
from fuzzywuzzy import fuzz

from app import app
from app.decorators import require_role
from app.forms.examination import EditForm
from app.models.examination import test_types
from app.roles import Roles
from app.service import role_service, examination_service
from app.utils.file import file_upload, file_remove

blueprint = Blueprint('examination', __name__, url_prefix='/examination')

UPLOAD_FOLDER = app.config['EXAMINATION_UPLOAD_FOLDER']

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'courses': 'course.view_courses'
               }


DATE_FORMAT = app.config['DATE_FORMAT']


@blueprint.route('/add/', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def add():
    form = EditForm(request.form)

    courses = examination_service.find_all_courses()
    educations = examination_service.find_all_educations()

    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    form.test_type.choices = test_types.items()

    if form.validate_on_submit():
        answer_filename = None
        exam_filename = None
        error = False

        exam_file = request.files.get('examination', None)
        answer_file = request.files.get('answers', None)

        # Exam file is required
        if exam_file:
            exam_path = file_upload(exam_file, UPLOAD_FOLDER)
            if not exam_path:
                error = True
            else:
                exam_filename = exam_path.name
        else:
            flash(_('No examination uploaded.'), 'danger')
            error = True

        # Answer file is optional
        if answer_file:
            answer_path = file_upload(answer_file, UPLOAD_FOLDER)
            if not answer_path:
                error = True
            else:
                answer_filename = answer_path.name
        else:
            flash(_('No answers uploaded.'), 'warning')

        if error:
            return render_template('examination/edit.htm',
                                   courses=courses,
                                   educations=educations,
                                   form=form,
                                   test_types=test_types, new_exam=True)
        else:
            examination_service.\
                add_examination(exam_filename, form.date.data,
                                form.comment.data, form.course.data,
                                form.education.data, answer_filename,
                                form.test_type.data)

            flash(_('Examination successfully uploaded.'), 'success')
            return redirect(url_for('examination.add', new_exam=True))

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

    form = EditForm(request.form, obj=exam)

    courses = examination_service.find_all_courses()
    educations = examination_service.find_all_educations()

    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    form.test_type.choices = test_types.items()

    if form.validate_on_submit():
        file = request.files['examination']
        answers = request.files['answers']

        date = form.date.data
        comment = form.comment.data
        course_id = form.course.data
        education_id = form.education.data
        test_type = form.test_type.data
        path = exam.path
        answer_path = exam.answer_path

        if file.filename:
            if exam.path:
                file_remove(exam.path, UPLOAD_FOLDER)
            new_path = file_upload(file, UPLOAD_FOLDER)
            if new_path:
                path = new_path.name
            else:
                flash(_('Wrong format examination or error ' +
                        'uploading the file.'), 'danger')

        if answers.filename:
            if exam.answer_path:
                file_remove(exam.answer_path, UPLOAD_FOLDER)
            new_answer_path = file_upload(answers, UPLOAD_FOLDER)
            if new_answer_path:
                answer_path = new_answer_path.name
            else:
                flash(_('Wrong format answers or error ' +
                        'uploading the file.'), 'danger')

        examination_service.update_examination(exam_id, path, date, comment,
                                               course_id, education_id,
                                               answer_path, test_type)
        flash(_('Examination successfully changed.'), 'success')

        return redirect(url_for('examination.edit', exam_id=exam_id))
    else:
        # Load the existing field values
        form.course.data = exam.course_id
        form.education.data = exam.education_id
        form.test_type.data = exam.test_type
        form.comment.data = exam.comment

    path = '/static/uploads/examinations/'

    return render_template('examination/edit.htm',
                           form=form, path=path,
                           examination=exam, title=_('Examinations'),
                           courses=courses, educations=educations,
                           new_exam=False)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def view_examination(page_nr=1):
    # First check if the delete argument is set before loading
    # the search results
    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = examination_service.get_examination_by_id(exam_id)

        if not examination:
            flash(_('Specified examination does not exist'), 'danger')
        else:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
            except OSError:
                flash(_('File does not exist, examination deleted.'), 'info')

            examination_service.delete_examination(exam_id)
            flash(_('Examination successfully deleted.'))

    # After deletion, do the search.
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

    path = '/static/uploads/examinations/'

    can_write = role_service.user_has_role(Roles.EXAMINATION_WRITE)

    return render_template('examination/view.htm', path=path,
                           examinations=examinations, search=search,
                           title=_('Examinations'), test_types=test_types,
                           can_write=can_write)
