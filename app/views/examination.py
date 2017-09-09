import os
import json

from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for
from flask_login import login_required
from flask_babel import _
from flask_sqlalchemy import Pagination
from fuzzywuzzy import fuzz

from app import app, db
from app.forms import CourseForm, EducationForm
from app.forms.examination import EditForm
from app.utils.file import file_upload, file_remove
from app.models.examination import Examination, test_types
from app.models.course import Course
from app.models.education import Education
from app.utils.module import ModuleAPI

blueprint = Blueprint('examination', __name__)

UPLOAD_FOLDER = app.config['EXAMINATION_UPLOAD_FOLDER']

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'examination.view_educations',
               'courses': 'examination.view_courses'
               }

DATE_FORMAT = app.config['DATE_FORMAT']


def get_education_id(education):
    education_object = db.session.query(Education) \
        .filter(Education.name == education).first()

    if not education_object:
        return None
    return education_object[0].id


def get_course_id(course):
    course_object = db.session.query(Course).filter(Course.name == course) \
        .first()

    if not course_object:
        return None
    return course_object.id


@blueprint.route('/examination/add/', methods=['GET', 'POST'])
@login_required
def add():
    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.add'
        return abort(403)

    form = EditForm(request.form, )

    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()
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
            db.session.add(exam)
            db.session.commit()

            flash(_('Examination successfully uploaded.'), 'success')
            return redirect(url_for('examination.edit', exam_id=exam.id))

    return render_template('examination/edit.htm', courses=courses,
                           educations=educations, new_exam=True,
                           form=form)


@blueprint.route('/examination/edit/<int:exam_id>/', methods=['GET', 'POST'])
@login_required
def edit(exam_id):
    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_examination'
        return abort(403)

    exam = Examination.query.get(exam_id)

    if not exam:
        flash(_('Examination could not be found.'), 'danger')
        return redirect(url_for('examination.view_examination'))

    session['examination_edit_id'] = exam_id

    form = EditForm(request.form, exam)

    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()
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


@blueprint.route('/examination/', methods=['GET', 'POST'])
@blueprint.route('/examination/<int:page_nr>/', methods=['GET', 'POST'])
@login_required
def view_examination(page_nr=1):
    if not ModuleAPI.can_read('examination', True):
        flash(_('Valid membership is required for the examination module'),
              'warning')
        session['prev'] = 'examination.view_examination'
        return abort(403)

    # First check if the delete argument is set before loading
    # the search results
    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = Examination.query.filter(Examination.id == exam_id) \
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
            # .order_by(func.field(Course.id, *ranked_courses)) \
            res = Examination.query.join(Course) \
                .filter(Course.id.in_(ranked_courses)) \
                .order_by(Examination.date.desc()) \
                .all()

            res = sorted(res, key=lambda i: ranked_courses.index(i.course.id))

            if page_nr is None:
                try:
                    page_nr = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    abort(404)

            index = (page_nr - 1) * 15

            examinations = Pagination(None, page_nr, 15, len(res),
                                      res[index:index + 15])

    else:
        search = ""
        # Query the exams. The order_by part makes sure the exams are sorted
        # by course and within a course are sorted by date
        examinations = Examination.query.join(Course) \
            .order_by(Course.name) \
            .order_by(Examination.date.desc()) \
            .paginate(page_nr, 15, True)

    path = '/static/uploads/examinations/'

    return render_template('examination/view.htm', path=path,
                           examinations=examinations, search=search,
                           title=_('Examinations'), test_types=test_types)


@blueprint.route('/courses/', methods=['GET'])
def view_courses():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    return render_template('course/view.htm')


@blueprint.route('/courses/api/get/', methods=['GET'])
def get_courses():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    courses = Course.query.all()
    courses_list = []

    for course in courses:
        courses_list.append(
            [course.id,
             course.name,
             course.description if course.description != "" else "N/A"
             ])

    return json.dumps({"data": courses_list})


@blueprint.route('/courses/add/', methods=['GET', 'POST'])
def add_course():
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.add_course'
        return abort(403)

    form = CourseForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            course = Course.query.filter(Course.name == title).first()
            if not course:
                description = form.description.data
                new_course = Course(title, description)
                db.session.add(new_course)
                db.session.commit()
                flash("'%s': " % title + _('Course succesfully added.'),
                      'success')
            else:
                flash("'%s': " % title + _('Already exists in the database'),
                      'danger')

                return render_template('course/edit.htm', new=True, form=form)

            if 'origin' in session:
                redir = session['origin']
            else:
                redir = url_for('examination.add')
            return redirect(redir)

    return render_template('course/edit.htm', new=True, form=form)


@blueprint.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_course'
        return abort(403)

    course = Course.query.get(course_id)

    if not course:
        flash(_('Course could not be found.'), 'danger')
        return redirect(url_for('examination.view_courses'))

    exam_count = Examination.query.filter(Examination.course == course).count()
    if 'delete' in request.args:
        if exam_count > 0:
            flash(_('Course still has examinations in the database.'),
                  'danger')
            form = CourseForm(title=course.name,
                              description=course.description)
            return render_template('course/edit.htm', new=False,
                                   form=form,
                                   course=course, redir=r,
                                   exam_count=exam_count)

        Course.query.filter_by(id=course_id).delete()
        db.session.commit()

        flash(_('Course succesfully deleted.'), 'success')
        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    if request.method == 'POST':
        form = CourseForm(request.form)
        if form.validate_on_submit():
            title = form.title.data
            if title != course.name and Course.query.filter(
                    Course.name == title).count() >= 1:
                flash("'%s': " % title + _('Already exists in the database'),
                      'danger')
                return render_template('course/edit.htm', new=False,
                                       form=form, redir=r,
                                       course=course,
                                       exam_count=exam_count)
            else:
                description = form.description.data
                course.name = title
                course.description = description

                db.session.commit()
                flash(_('Course succesfully saved.'),
                      'success')

                if 'origin' in session:
                    redir = session['origin']
                else:
                    redir = url_for('examination.add')
                return redirect(redir)
    else:
        form = CourseForm(title=course.name, description=course.description)

    return render_template('course/edit.htm', new=False,
                           form=form, redir=r, course=course,
                           exam_count=exam_count)


@blueprint.route('/educations/', methods=['GET'])
def view_educations():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    return render_template('education/view.htm')


@blueprint.route('/educations/api/get/', methods=['GET'])
def get_educations():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    educations = Education.query.all()
    educations_list = []

    for education in educations:
        created = "N/A"
        modified = "N/A"
        if education.created:
            created = education.created.strftime(DATE_FORMAT)

        if education.modified:
            modified = education.modified.strftime(DATE_FORMAT)

        educations_list.append(
            [education.id,
             education.name,
             created,
             modified
             ])

    return json.dumps({"data": educations_list})


@blueprint.route('/education/add/', methods=['GET', 'POST'])
def add_education():
    r = request.args.get('redir', True)
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.add_education'
        return abort(403)

    form = EducationForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            education = Education.query.filter(Education.name == title).first()
            if not education:
                new_education = Education(title)

                db.session.add(new_education)
                db.session.commit()
                flash("'%s': " % title + _('Education succesfully added.'),
                      'success')
            else:
                flash("'%s': " % title + _('Already exists in the database'),
                      'danger')

            if 'origin' in session:
                redir = session['origin']
            else:
                redir = url_for('examination.add')
            return redirect(redir)

    return render_template('education/edit.htm',
                           form=form, new=True)


@blueprint.route('/education/edit/<int:education_id>', methods=['GET', 'POST'])
def edit_education(education_id):
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_education'
        return abort(403)

    education = Education.query.get(education_id)

    if not education:
        flash(_('Education could not be found.'), 'danger')
        return redirect(url_for('examination.view_educations'))

    exam_count = Examination.query.filter(
        Examination.education == education).count()

    if 'delete' in request.args:
        if exam_count > 0:
            flash(_('Education still has examinations in the database.'),
                  'danger')
            form = CourseForm(title=education.name)
            return render_template('education/edit.htm', new=False,
                                   form=form, education=education,
                                   redir=r, exam_count=exam_count)

        Education.query.filter_by(id=education_id).delete()
        db.session.commit()

        flash(_('Education succesfully deleted.'), 'success')
        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    if request.method == 'POST':
        form = EducationForm(request.form)
        if form.validate_on_submit():
            name = form.title.data
            if name != education.name and Education.query.filter(
                    Education.name == name).count() >= 1:
                flash("'%s': " % name + _('Already exists in the database'),
                      'danger')
                return render_template('education/edit.htm', new=False,
                                       form=form, redir=r,
                                       exam_count=exam_count,
                                       education=education)
            else:
                education.name = name

                db.session.commit()
                flash("'%s': " % name + _('Education succesfully saved.'),
                      'success')

                if 'origin' in session:
                    redir = session['origin']
                else:
                    redir = url_for('examination.view_educations')
                return redirect(redir)

    else:
        form = CourseForm(title=education.name)

    return render_template('education/edit.htm', new=False,
                           form=form, redir=r, exam_count=exam_count,
                           education=education)
