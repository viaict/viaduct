from flask import Blueprint
from flask import flash, session, redirect, render_template, request, \
    url_for
from flask_babel import _

from app import app
from app.forms.examination import EducationForm
from app.exceptions import BusinessRuleException, DuplicateResourceException
from app.roles import Roles
from app.decorators import require_role
from app.service import examination_service

import json

blueprint = Blueprint('education', __name__, url_prefix='/education')

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'education.view_educations',
               'courses': 'course.view_courses'
               }

DATE_FORMAT = app.config['DATE_FORMAT']


@blueprint.route('/', methods=['GET'])
@require_role(Roles.EXAMINATION_WRITE)
def view_educations():
    return render_template('education/view.htm')


@blueprint.route('/api/get/', methods=['GET'])
@require_role(Roles.EXAMINATION_WRITE)
def get_educations():
    educations = examination_service.find_all_educations()
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


@blueprint.route('/add/', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def add_education():
    r = request.args.get('redir', True)
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    form = EducationForm(request.form)

    if form.validate_on_submit():
        name = form.title.data
        try:
            examination_service.add_education(name)
            flash("'%s': " % name + _('Education successfully added.'),
                  'success')
        except DuplicateResourceException as e:
            flash("'%s': " % name + _('Already exists in the database'),
                  'danger')

        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    return render_template('education/edit.htm',
                           form=form, new=True)


@blueprint.route('/edit/<int:education_id>', methods=['GET', 'POST'])
@require_role(Roles.EXAMINATION_WRITE)
def edit_education(education_id):
    r = request.args.get('redir')
    if r in REDIR_PAGES:
        session['origin'] = url_for(REDIR_PAGES[r])
    elif r == 'edit' and 'examination_edit_id' in session:
        session['origin'] = '/examination/edit/{}'.format(
            session['examination_edit_id'])

    education = examination_service.get_education_by_id(education_id)
    exam_count = examination_service.\
        count_examinations_by_education(education_id)

    if 'delete' in request.args:
        try:
            examination_service.delete_education(education_id)
            flash(_('Education successfully deleted.'), 'success')
        except BusinessRuleException as e:
            flash(_(e.detail), 'danger')
            form = EducationForm(title=education.name)
            return render_template('education/edit.htm', new=False,
                                   form=form, education=education,
                                   redir=r, exam_count=exam_count)

        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('examination.add')
        return redirect(redir)

    form = EducationForm(request.form)

    if form.validate_on_submit():
        name = form.title.data
        try:
            examination_service.update_education(education_id, name)
            flash("'%s': " % name + _('Education successfully saved.'),
                  'success')
        except DuplicateResourceException as e:
            flash("%s: " % e, 'danger')

        if 'origin' in session:
            redir = session['origin']
        else:
            redir = url_for('education.view_educations')
        return redirect(redir)

    else:
        form = EducationForm(title=education.name)

    return render_template('education/edit.htm', new=False,
                           form=form, redir=r, exam_count=exam_count,
                           education=education)
