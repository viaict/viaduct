import os

from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for
from flask_login import login_required
from flask_babel import _

from sqlalchemy import func

from app import app, db

from app.forms.summary import EditForm
from app.utils.forms import flash_form_errors

from app.models.summary import Summary
from app.models.course import Course
from app.models.education import Education

from app.utils.module import ModuleAPI

from werkzeug import secure_filename

from fuzzywuzzy import fuzz

blueprint = Blueprint('summary', __name__, url_prefix='/summary')

UPLOAD_FOLDER = app.config['SUMMARY_UPLOAD_FOLDER']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

DATE_FORMAT = app.config['DATE_FORMAT']


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_exists(filename):
    return os.path.exists(os.path.join(UPLOAD_FOLDER, filename))


def create_unique_file(filename):
    temp_filename = filename

    i = 0
    while file_exists(temp_filename):
        split = filename.split('.')
        split[0] = split[0] + "(" + str(i) + ")"
        temp_filename = split[0] + "." + split[len(split) - 1]
        i += 1
    return temp_filename


def get_education_id(education):
    education_object = db.session.query(Education)\
        .filter(Education.name == education).first()

    if not education_object:
        return None
    return education_object[0].id


def get_course_id(course):
    course_object = db.session.query(Course).filter(Course.name == course)\
        .first()

    if not course_object:
        return None
    return course_object.id


def upload_file_real(file, old_path='1'):
    if file and (file.filename is not ''):
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = create_unique_file(filename)

            if old_path != '1':
                os.remove(os.path.join(UPLOAD_FOLDER, old_path))

            file.save(os.path.join(UPLOAD_FOLDER, filename))

            return filename
        else:
            return None
    else:
        return False


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
# @login_required
def view(page_nr=1):
    if not ModuleAPI.can_read('summary', True):
        flash(_('Valid membership is required for the summary module'),
              'warning')
        session['prev'] = 'summary.view'
        return abort(403)

    # First check if the delete argument is set before loading
    # the search results
    if request.form.get('delete') and request.method == 'POST':
        summary_id = request.form.get('delete')
        summary = Summary.query.filter(Summary.id == summary_id)\
            .first()

        if not summary:
            flash(_('Specified summary to delete does not exist'), 'danger')
        else:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, summary.path))
            except:
                flash(_('File does not exist, summary deleted.'), 'info')

            db.session.delete(summary)
            db.session.commit()
            flash(_('Summary successfully deleted.'))
            redir_url = url_for('summary.view', page_nr=page_nr)
            if request.args.get('search'):
                redir_url += ("?search=" + request.args.get('search'))
            return redirect(redir_url)

    if request.args.get('search'):
        search = request.args.get('search')

        summaries = Summary.query.all()
        summary_matches_per_course = {}
        course_max_scores = {}

        search_lower = search.lower().strip()

        for summary in summaries:
            course = summary.course.name.lower()
            title_ratio = fuzz.partial_ratio(
                search_lower, summary.title.lower())
            course_ratio = fuzz.partial_ratio(search_lower, course)
            education_ratio = fuzz.partial_ratio(
                search_lower, summary.education.name.lower())
            if title_ratio > 75 or course_ratio > 75 or education_ratio > 75:
                # Calculate the score for the summary
                # TODO: maybe use a weighted mean instead of max
                score = max(title_ratio, course_ratio, education_ratio)

                summary_tuple = (score, summary.id)

                # If the course did not occur before, add it
                # to the dictionaries and set the max score
                # to the score of this summary
                if course not in summary_matches_per_course:
                    summary_matches_per_course[course] = [summary_tuple]
                    course_max_scores[course] = score

                # Otherwise, add the summary to the list of the course
                # and update the maximum course score
                else:
                    summary_matches_per_course[course].append(summary_tuple)
                    course_max_scores[course] = max(score,
                                                    course_max_scores[course])
        if len(course_max_scores) == 0:
            summaries = None
        else:
            # Sort the courses by their max score
            courses_sorted = sorted(course_max_scores,
                                    key=course_max_scores.get, reverse=True)

            # Create the list of summary ids. These are ordered by course with
            # their maximum score, and for each course ordered by summary score
            summary_matches = []
            for course in courses_sorted:
                summary_matches.extend(list(zip(*sorted(
                    summary_matches_per_course[course], reverse=True)))[1])

            # Query the summaries. The order_by clause keeps them in the same
            # order as the summary_matches list
            summaries = Summary.query \
                .filter(Summary.id.in_(summary_matches)) \
                .order_by(func.field(Summary.id, *summary_matches)) \
                .paginate(page_nr, 15, True)
    else:
        search = ""
        summaries = Summary.query.join(Course)\
            .order_by(Course.name).paginate(page_nr, 15, True)

    path = '/static/uploads/summaries/'

    return render_template('summary/view.htm', path=path,
                           summaries=summaries, search=search,
                           title=_('Summaries'))


@blueprint.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    if not ModuleAPI.can_write('summary', True):
        session['prev'] = 'summary.edit_summary'
        return abort(403)

    form = EditForm(request.form)
    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()
    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]
    path = '/static/uploads/summaries/'

    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['summary']

            new_path = upload_file_real(file)
            if new_path:
                summary = Summary(form.title.data, new_path,
                                  form.date.data, form.course.data,
                                  form.education.data)

                db.session.add(summary)
                db.session.commit()
                flash(_('Summary uploaded succesfully.'), 'success')
            elif new_path is None:
                flash(_('Wrong format summary.'), 'danger')

            if not new_path:
                flash(_('Summary required.'), 'danger')
                return render_template(
                    'summary/edit.htm', path=path,
                    courses=courses, educations=educations,
                    new_summary=True, form=form)

            return redirect(url_for('summary.edit', summary_id=summary.id))
        else:
            flash_form_errors(form)

    return render_template(
        'summary/edit.htm', path=path,
        courses=courses, educations=educations,
        new_summary=True, form=form)


@blueprint.route('/edit/<int:summary_id>/', methods=['GET', 'POST'])
@login_required
def edit(summary_id):
    if not ModuleAPI.can_write('summary', True):
        session['prev'] = 'summary.edit_summary'
        return abort(403)

    summary = Summary.query.get(summary_id)

    if not summary:
        flash(_('Summary could not be found.'), 'danger')
        return redirect(url_for('summary.view'))

    session['summary_edit_id'] = summary_id

    form = EditForm(request.form, summary)
    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()
    form.course.choices = [(c.id, c.name) for c in courses]
    form.education.choices = [(e.id, e.name) for e in educations]

    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['summary']

            summary.title = form.title.data
            summary.course_id = form.course.data
            summary.education_id = form.education.data
            summary.date = form.date.data

            new_path = upload_file_real(file, summary.path)
            if new_path:
                summary.path = new_path
            elif new_path is None:
                flash(_('Wrong format summary.'), 'danger')

            if not new_path:
                flash(_('Old summary preserved.'), 'info')

            db.session.commit()
            flash(_('Summary succesfully changed.'), 'success')

            return redirect(url_for('summary.edit', summary_id=summary_id))
        else:
            flash_form_errors(form)

    path = '/static/uploads/summaries/'

    return render_template(
        'summary/edit.htm', path=path, summary=summary,
        courses=courses, educations=educations,
        new_summary=False, form=form)
