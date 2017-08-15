from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for
from flask_babel import _

from app import db
from app.forms import CourseForm
from app.models.examination import Examination
from app.models.course import Course
from app.utils.module import ModuleAPI

import json


blueprint = Blueprint('course', __name__, url_prefix='/courses')

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'education.view_educations',
               'courses': 'course.view_courses'
               }


@blueprint.route('/', methods=['GET'])
def view_courses():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    return render_template('course/view.htm')


@blueprint.route('/api/get/', methods=['GET'])
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


@blueprint.route('/add/', methods=['GET', 'POST'])
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


@blueprint.route('/edit/<int:course_id>', methods=['GET', 'POST'])
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
