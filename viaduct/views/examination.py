import os
from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request, \
    url_for, jsonify
from flask.ext.login import login_required

from sqlalchemy import or_

from viaduct import application, db

from viaduct.forms import CourseForm
from viaduct.helpers import flash_form_errors
from viaduct.forms import EducationForm
from viaduct.utilities import serialize_sqla

from viaduct.models.examination import Examination
from viaduct.models.course import Course
from viaduct.models.education import Education
from viaduct.models.degree import Degree

from viaduct.api.module import ModuleAPI

from werkzeug import secure_filename

blueprint = Blueprint('examination', __name__)

UPLOAD_FOLDER = application.config['EXAMINATION_UPLOAD_FOLDER']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


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
            print('Wrong file!')
            return None
    else:
        print('No file uploaded')
        return False


@blueprint.route('/examination/add/', methods=['GET', 'POST'])
def upload_file():
    if not ModuleAPI.can_write('examination'):
        session['prev'] = 'examination.upload_file'
        return abort(403)

    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()
    degrees = Degree.query.order_by(Degree.name).all()

    if request.method == 'POST':
        file = request.files.get('file', None)
        answers = request.files.get('answers', None)
        title = request.form.get("title", None)
        course_id = request.form.get("course", None)
        education_id = request.form.get("education", None)

        error = False

        if not title:
            flash('Geen titel opgegeven', 'danger')
            error = True

        print(answers)
        filename = upload_file_real(file)
        if file:
            if not filename:
                flash('Fout formaat tentamen', 'danger')
                error = True

            answer_path = upload_file_real(answers)
            if answer_path is False:
                flash('Geen antwoorden geupload', 'danger')
                answer_path = 1
            elif answer_path is None:
                flash('Fout formaat antwoord', 'danger')
                error = True
        else:
            flash('Geen tentamen opgegeven', 'danger')
            error = True

        if error:
            return render_template('examination/upload.htm', courses=courses,
                                   educations=educations, message='',
                                   title='Tentamens', degrees=degrees)

        exam = Examination(filename, title, course_id, education_id,
                           answers=answer_path)
        db.session.add(exam)
        db.session.commit()

        flash('Het tentamen is geupload', 'success')

        return render_template('examination/upload.htm', courses=courses,
                               educations=educations, message='',
                               title='Tentamens', degrees=degrees)

    return render_template('examination/upload.htm', courses=courses,
                           educations=educations, title='Tentamens',
                           degrees=degrees)


@blueprint.route('/examination/', methods=['GET', 'POST'])
@blueprint.route('/examination/<int:page_nr>/', methods=['GET', 'POST'])
@login_required
def view_examination(page_nr=1):
    if not ModuleAPI.can_read('examination', False):
        session['prev'] = 'examination.view_examination'
        return abort(403)

    # action = url_for('examination.view_examination')

    path = '/static/uploads/examinations/'

    if request.args.get('search'):
        search = request.args.get('search')

        examinations = Examination.query.join(Course).join(Education)\
            .filter(or_(Examination.title.like('%' + search + '%'),
                        Course.name.like('%' + search + '%'),
                        Education.name.like('%' + search + '%')))\
            .order_by(Course.name).paginate(page_nr, 15, True)
        return render_template('examination/view.htm', path=path,
                               examinations=examinations, search=search,
                               title='Tentamens')

    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = Examination.query.filter(Examination.id == exam_id)\
            .first()

        try:
            os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
        except:
            flash('File bestaat niet, tentamen is verwijderd', 'info')

        title = examination.title
        db.session.delete(examination)
        db.session.commit()
        examinations = Examination.query.paginate(page_nr, 15, False)
        return render_template('examination/admin.htm', path=path,
                               examinations=examinations, search="",
                               message="Tentamen " + title +
                                       " succesvol verwijderd",
                               title='Tentamens')

    examinations = Examination.query.join(Course)\
        .order_by(Course.name).paginate(page_nr, 15, True)
    return render_template('examination/view.htm', path=path,
                           examinations=examinations, search="",
                           title='Tentamens')


@blueprint.route('/examination/admin/', methods=['GET', 'POST'])
@blueprint.route('/examination/admin/<int:page_nr>/', methods=['GET', 'POST'])
def examination_admin(page_nr=1):
    if not ModuleAPI.can_write('examination', False):
        session['prev'] = 'examination.examination_admin'
        return abort(403)

    path = '/static/uploads/examinations/'

    if request.args.get('search'):
        search = request.args.get('search')
        examinations = Examination.query.join(Course).join(Education)\
            .filter(or_(Examination.title.like('%' + search + '%'),
                        Course.name.like('%' + search + '%'),
                        Education.name.like('%' + search + '%')))\
            .paginate(page_nr, 15, False)
        return render_template('examination/admin.htm', path=path,
                               examinations=examinations, search=search,
                               message="", title='Tentamens')

    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = Examination.query.filter(Examination.id == exam_id)\
            .first()

        os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
        title = examination.title
        db.session.delete(examination)
        db.session.commit()
        examinations = Examination.query.paginate(page_nr, 15, False)
        return render_template('examination/admin.htm', path=path,
                               examinations=examinations, search="",
                               message="Tentamen " + title +
                                       " succesvol verwijderd",
                               title='Tentamens')

    if request.args.get('edit'):
        exam_id = request.args.get('edit')
        examination = Examination.query.filter(Examination.id == exam_id)\
            .first()

        os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
        db.session.delete(examination)
        db.session.commit()

    examinations = Examination.query.paginate(page_nr, 15, False)
    return render_template('examination/admin.htm', path=path,
                           examinations=examinations, search="", message="",
                           title='Tentamens')


@blueprint.route('/examination/edit/<int:exam_id>/', methods=['GET', 'POST'])
@login_required
def edit(exam_id):
    if not ModuleAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_examination'
        return abort(403)

    exam = Examination.query.get(exam_id)

    if request.method == 'POST':
        file = request.files['file']
        answers = request.files['answers']
        title = request.form.get("title", None)
        course_id = request.form.get("course", None)
        education_id = request.form.get("education", None)

        if not title:
            flash('Geen titel opgegeven', 'danger')
        elif not education_id:
            flash('Geen opleiding opgegeven', 'danger')
        else:
            exam.title = title
            exam.course_id = course_id
            exam.education_id = education_id

            new_path = upload_file_real(file, exam.path)
            if new_path:
                exam.path = new_path
            elif new_path is None:
                flash('Fout formaat tentamen', 'danger')

            if not new_path:
                flash('Oude tentamen bewaard', 'success')

            new_answer_path = upload_file_real(answers, exam.answer_path)
            if new_answer_path:
                exam.answer_path = new_answer_path
            elif new_answer_path is None:
                flash('Fout formaat antwoorden', 'danger')

            if not new_answer_path:
                flash('Oude antwoorden bewaard', 'success')

            db.session.commit()
            flash('Het tentamen is aangepast!', 'success')

            return redirect(url_for('examination.edit', exam_id=exam_id))

    path = '/static/uploads/examinations/'
    courses = Course.query.order_by(Course.name).all()
    educations = Education.query.order_by(Education.name).all()

    return render_template(
        'examination/edit.htm', path=path, examination=exam, title='Tentamens',
        courses=courses, educations=educations)


@blueprint.route('/course/add/', methods=['GET', 'POST'])
def add_course():
    if not ModuleAPI.can_write('examination'):
        session['prev'] = 'examination.add_course'
        return abort(403)

    form = CourseForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            course = form.title.data
            description = form.description.data
            new_course = Course(course, description)
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('examination.upload_file'))
        else:
            flash_form_errors(form)

    return render_template('examination/course.htm',
                           title='Tentamens',
                           form=form)


@blueprint.route('/education/add/', methods=['GET', 'POST'])
def add_education():
    if not ModuleAPI.can_write('examination'):
        session['prev'] = 'examination.add_education'
        return abort(403)

    form = EducationForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            education = Education.query.filter(Education.name == title).first()
            if not education:
                new_education = Education(1, title)

                db.session.add(new_education)
                db.session.commit()
                flash('Studie succesvol toegevoegd', 'success')
            else:
                flash('%s: bestaat al in de database' % title, 'danger')
            return redirect(url_for('examination.upload_file'))

        else:
            flash_form_errors(form)

    return render_template('examination/education.htm',
                           title='Tentamens',
                           form=form)


@blueprint.route('/examination/api/course/', methods=['POST'])
def examination_api_course_add():
    if not ModuleAPI.can_write('examination'):
        return abort(403)

    course_name = request.form.get('course_name', '')

    if course_name == '':
        return jsonify(error='Geen vaknaam opgegeven'), 500

    course = Course(course_name, '')
    db.session.add(course)
    db.session.commit()

    courses = Course.query.order_by(Course.name).all()

    return jsonify(course_id=course.id, courses=serialize_sqla(courses))


@blueprint.route('/examination/api/education/', methods=['POST'])
def examination_api_education_add():
    if not ModuleAPI.can_write('examination'):
        return abort(403)

    education_name = request.form.get('education_name', '')
    degree_id = request.form.get('degree_id', '')

    if education_name == '':
        return jsonify(error='Geen opleidingnaam opgegeven'), 500
    if degree_id == '':
        return jsonify(error='Geen opleidinggraad opgegeven'), 500

    education = Education(degree_id, education_name)
    db.session.add(education)
    db.session.commit()

    educations = Education.query.order_by(Education.name).all()

    return jsonify(education_id=education.id,
                   educations=serialize_sqla(educations))
