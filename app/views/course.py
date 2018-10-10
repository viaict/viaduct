from flask import Blueprint
from flask import flash, session, redirect, render_template, request, \
    url_for
from flask_babel import _

from app.decorators import require_role
from app.exceptions.base import DuplicateResourceException
from app.forms.examination import CourseForm
from app.roles import Roles
from app.service import examination_service

blueprint = Blueprint('course', __name__, url_prefix='/courses')

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'education.view_educations',
               'courses': 'course.view_courses'
               }


@blueprint.route('/', methods=['GET'])
@require_role(Roles.EXAMINATION_WRITE)
def view_courses():
    return render_template('course/view.htm')


@blueprint.route('/add/', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def add_course():
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    form = CourseForm(request.form)

    if form.validate_on_submit():
        name = form.title.data
        description = form.description.data
        try:
            examination_service.add_course(name, description)
            flash("'%s': " % form.title.data + _('Course successfully added.'),
                  'success')
        except DuplicateResourceException as e:
            flash(_('Course \'%s\'' % e.resource + ' already in database.'),
                  'danger')

            return render_template('course/edit.htm', new=True, form=form)

        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    return render_template('course/edit.htm', new=True, form=form)


@blueprint.route('/edit/<int:course_id>', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def edit_course(course_id):
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    course = examination_service.get_course_by_id(course_id)
    exam_count = examination_service.count_examinations_by_course(course)

    form = CourseForm(request.form)
    if form.validate_on_submit():
        name = form.title.data
        description = form.description.data
        try:
            examination_service.update_course(course_id, name, description)
            flash(_('Course successfully saved.'), 'success')
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
