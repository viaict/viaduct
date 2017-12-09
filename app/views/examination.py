import os

from flask import Blueprint
from flask import flash, session, redirect, render_template, request, url_for
from flask_babel import gettext as _
from fuzzywuzzy import fuzz
from sqlalchemy import func

from app import app, db
from app.decorators import require_role
from app.forms.examination import EditForm
from app.models.course import Course
from app.models.examination import Examination, test_types
from app.roles import Roles
from app.service import role_service, examination_service
from app.utils.file import file_upload, file_remove

blueprint = Blueprint('examination', __name__, url_prefix='/examination')

UPLOAD_FOLDER = app.config['EXAMINATION_UPLOAD_FOLDER']

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'examination.view_educations',
               'courses': 'course.view_courses'
               }


DATE_FORMAT = app.config['DATE_FORMAT']


@blueprint.route('/add/', methods=['GET', 'POST'])
# @require_membership
@require_role(Roles.EXAMINATION_WRITE)
def add():
    form = EditForm(request.form)

    courses = examination_service.find_all_courses()
    educations = examination_service.find_all_educations()

    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    form.test_type.choices = test_types.items()

    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files.get('examination', None)
            answers = request.files.get('answers', None)

            error = False

            exam_path = file_upload(file, UPLOAD_FOLDER)
            answers_path = None
            if file:
                if not exam_path:
                    flash(_('Wrong format examination.'), 'danger')
                    error = True

                if answers:
                    answers_file = file_upload(answers, UPLOAD_FOLDER)
                    if answers_file is False:
                        flash(_('No answers uploaded.'), 'warning')
                        answers_file = None
                    elif answers_file is None:
                        flash(_('Wrong format answers.'), 'danger')
                        error = True
                    else:
                        answers_path = answers_file.name
                else:
                    flash(_('No answers uploaded.'), 'warning')
                    answers_path = None
            else:
                flash(_('No examination uploaded.'), 'danger')
                error = True

            if error:
                # The upload has failed, but a dummy exam is created to
                # re-populate the form with the data the user provided before

                # Not the complete set of data is displayed again in the newly
                # rendered form, the course and study are reset. Reported in
                # Jira as VIA-1637 - DvE, 14-01-2017
                dummy_exam = Examination(file.name, form.date.data,
                                         form.comment.data, form.course.data,
                                         form.education.data,
                                         test_type=form.test_type.data)

                return render_template('examination/edit.htm',
                                       courses=courses,
                                       educations=educations,
                                       examination=dummy_exam,
                                       form=form,
                                       test_types=test_types, new_exam=False)

            exam = Examination(exam_path.name, form.date.data,
                               form.comment.data, form.course.data,
                               form.education.data, answers=answers_path,
                               test_type=form.test_type.data)

            examination_service.create_examination(exam)

            flash(_('Examination successfully uploaded.'), 'success')
            return redirect(url_for('examination.edit', exam_id=exam.id))

    return render_template('examination/edit.htm', courses=courses,
                           educations=educations, new_exam=True,
                           form=form)


@blueprint.route('/edit/<int:exam_id>/', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
# @require_membership
def edit(exam_id):
    exam = Examination.query.get(exam_id)

    if not exam:
        flash(_('Examination could not be found.'), 'danger')
        return redirect(url_for('examination.view_examination'))

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

        exam.date = form.date.data
        exam.comment = form.comment.data
        exam.course_id = form.course.data
        exam.education_id = form.education.data
        exam.test_type = form.test_type.data

        if file.filename:
            if exam.path:
                file_remove(exam.path, UPLOAD_FOLDER)
            new_path = file_upload(file, UPLOAD_FOLDER)
            if new_path:
                exam.path = new_path.name
            else:
                flash(_('Wrong format examination or error ' +
                        'uploading the file.'), 'danger')

        if answers.filename:
            if exam.answer_path:
                file_remove(exam.answer_path, UPLOAD_FOLDER)
            new_answer_path = file_upload(answers, UPLOAD_FOLDER)
            if new_answer_path:
                exam.answer_path = new_answer_path.name
            else:
                flash(_('Wrong format answers or error ' +
                        'uploading the file.'), 'danger')

        db.session.commit()
        flash(_('Examination succesfully changed.'), 'success')

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
# @require_membership
def view_examination(page_nr=1):
    # First check if the delete argument is set before loading
    # the search results
    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = Examination.query.filter(Examination.id == exam_id)\
            .first()

        if not examination:
            flash(_('Specified examination does not exist'), 'danger')
        else:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
            except OSError:
                flash(_('File does not exist, examination deleted.'), 'info')

            db.session.delete(examination)
            db.session.commit()
            flash(_('Examination successfully deleted.'))

    # After deletion, do the search.
    if request.args.get('search'):
        search = request.args.get('search')

        courses = Course.query.all()
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
            examinations = Examination.query.join(Course)\
                .filter(Course.id.in_(ranked_courses)) \
                .order_by(func.field(Course.id, *ranked_courses)) \
                .order_by(Examination.date.desc()) \
                .paginate(page_nr, 15, True)
    else:
        search = ""
        # Query the exams. The order_by part makes sure the exams are sorted
        # by course and within a course are sorted by date
        examinations = Examination.query.join(Course)\
            .order_by(Course.name) \
            .order_by(Examination.date.desc()) \
            .paginate(page_nr, 15, True)

    path = '/static/uploads/examinations/'

    can_write = role_service.user_has_role(Roles.EXAMINATION_WRITE)

    return render_template('examination/view.htm', path=path,
                           examinations=examinations, search=search,
                           title=_('Examinations'), test_types=test_types,
                           can_write=can_write)
