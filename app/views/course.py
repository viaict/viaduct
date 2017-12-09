from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for
from flask_babel import _

from app.forms import CourseForm
# from app.models.course import Course
from app.service import examination_service
from app.utils.module import ModuleAPI
from app.exceptions import BusinessRuleException, DuplicateResourceException

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

    courses = examination_service.find_all_courses()
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

    if form.validate_on_submit():
        name = form.title.data
        description = form.description.data
        try:
            examination_service.add_course(name, description)
            flash("'%s': " % form.title.data + _('Course succesfully added.'),
                  'success')
        except DuplicateResourceException as e:
            flash('Course \'%s\'' % e.resource + ' already in database.',
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

    course = examination_service.get_course_by_id(course_id)
    exam_count = examination_service.count_examinations_by_course(course_id)
    if 'delete' in request.args:
        try:
            examination_service.delete_course(course_id)
            flash(_('Course succesfully deleted.'), 'success')
        except BusinessRuleException as e:
            flash(_(e.detail), 'danger')

            form = CourseForm(title=course.name,
                              description=course.description)
            return render_template('course/edit.htm', new=False,
                                   form=form,
                                   course=course, redir=r,
                                   exam_count=exam_count)

        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    form = CourseForm(request.form)
    if form.validate_on_submit():
        name = form.title.data
        description = form.description.data
        try:
            examination_service.update_course(course_id, name, description)
            flash(_('Course succesfully saved.'), 'success')
            return render_template('course/edit.htm', new=False,
                                   form=form, redir=r,
                                   course=course,
                                   exam_count=exam_count)
        except DuplicateResourceException as e:
            flash("%s: " % e, 'danger')

    else:
        form = CourseForm(title=course.name, description=course.description)

    return render_template('course/edit.htm', new=False,
                           form=form, redir=r, course=course,
                           exam_count=exam_count)
