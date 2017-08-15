from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for
from flask_babel import _

from app import app, db
from app.forms import CourseForm, EducationForm
from app.models.examination import Examination
from app.models.education import Education
from app.utils.module import ModuleAPI

import json

blueprint = Blueprint('education', __name__, url_prefix='/education')

UPLOAD_FOLDER = app.config['EXAMINATION_UPLOAD_FOLDER']

REDIR_PAGES = {'view': 'examination.view_examination',
               'add': 'examination.add',
               'educations': 'education.view_educations',
               'courses': 'course.view_courses'
               }

DATE_FORMAT = app.config['DATE_FORMAT']


@blueprint.route('/', methods=['GET'])
def view_educations():
    if not ModuleAPI.can_write('examination', True):
        return abort(403)

    return render_template('education/view.htm')


@blueprint.route('/api/get/', methods=['GET'])
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


@blueprint.route('/add/', methods=['GET', 'POST'])
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


@blueprint.route('/edit/<int:education_id>', methods=['GET', 'POST'])
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
