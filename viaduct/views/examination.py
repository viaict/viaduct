import os
from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request
from flask.ext.login import login_required

from sqlalchemy import or_

from viaduct import application, db

from viaduct.models.examination import Examination
from viaduct.models.course import Course
from viaduct.models.education import Education

from viaduct.api.group import GroupPermissionAPI

from werkzeug import secure_filename

blueprint = Blueprint('examination', __name__)

UPLOAD_FOLDER = application.config['EXAMINATION_UPLOAD_FOLDER']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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


@blueprint.route('/examination/add', methods=['GET', 'POST'])
def upload_file():
    if not GroupPermissionAPI.can_write('examination'):
        session['prev'] = 'examination.upload_file'
        return abort(403)

    courses = Course.query.all()
    educations = Education.query.all()

    if request.method == 'POST':
        file = request.files['file']
        answers = request.files['answers']
        title = request.form.get("title", None)
        course_id = request.form.get("course", None)
        education_id = request.form.get("education", None)

        error = False

        # course_id = get_course_id(course);
        # if(course_id == None):
        #   return render_template('examination/upload.htm', courses = courses,
        #   educations = educations, message = 'Er is een fout opgetreden!');
        # education_id = get_education_id(education)
        # if(education_id == None):
        #   return render_template('examination/upload.htm', courses = courses,
        #   educations = educations, message = 'Er is een fout opgetreden!');

        if not title:
            flash('Geen titel opgegeven', 'danger')
            error = True

        filename = upload_file_real(file)
        if file:
            if not filename:
                flash('Fout formaat tentamen', 'danger')
                error = True
            answer_path = upload_file_real(answers)
            if not answer_path:
                flash('Fout formaat antwoorden', 'danger')
                error = True
        else:
            flash('Geen tentamen opgegeven', 'danger')
            error = True

        if error:
            return render_template('examination/upload.htm', courses=courses,
                                   educations=educations, message='',
                                   title='Tentamens')

        exam = Examination(filename, title, course_id, education_id,
                           answers=answer_path)
        db.session.add(exam)
        db.session.commit()

        flash('Het tentamen is geupload', 'success')

        return render_template('examination/upload.htm', courses=courses,
                               educations=educations, message='',
                               title='Tentamens')

    return render_template('examination/upload.htm', courses=courses,
                           educations=educations, title='Tentamens')


@blueprint.route('/examination/', methods=['GET', 'POST'])
@blueprint.route('/examination/<int:page_nr>/', methods=['GET', 'POST'])
@login_required
def view_examination(page_nr=1):
    if not GroupPermissionAPI.can_read('examination', False):
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


@blueprint.route('/examination/admin', methods=['GET', 'POST'])
@blueprint.route('/examination/admin/<int:page_nr>/', methods=['GET', 'POST'])
def examination_admin(page_nr=1):
    if not GroupPermissionAPI.can_write('examination', False):
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


@blueprint.route('/examination/edit', methods=['GET', 'POST'])
@login_required
def edit_examination():
    if not GroupPermissionAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_examination'
        return abort(403)

    path = '../static/'

    courses = Course.query.all()
    educations = Education.query.all()
    message = False

    if request.method == 'POST':
        file = request.files['file']
        answers = request.files['answers']
        title = request.form.get("title", None)
        course_id = request.form.get("course", None)
        education_id = request.form.get("education", None)
        exam_id = request.form.get("examination", None)

        if not title:
            flash('Geen titel opgegeven', 'danger')
            print("wut")

        if title and education_id and exam_id:
            examination = Examination.query.filter(Examination.id == exam_id)\
                .first()

            examination.title = title
            examination.course_id = course_id
            examination.education_id = education_id

            if not title:
                flash('Geen titel opgegeven', 'danger')

            if file.name:
                examination.path = upload_file_real(file, examination.path)
                if not examination.path:
                    flash('Fout formaat tentamen', 'danger')
            else:
                flash('Geen tentamen opgegeven', 'danger')

            if answers:
                examination.answer_path = upload_file_real(answers)
                if not examination.answer_path:
                    flash('Fout formaat antwoorden', 'danger')
                if examination.answer_path:
                    examination.answer_path = None

            if message:
                return render_template('examination/edit.htm', courses=courses,
                                       educations=educations,
                                       examination=examination, message='',
                                       title='Tentamens')

            # if file:
            #   if allowed_file(file.filename):
            #       filename = secure_filename(file.filename)
            #       filename = create_unique_file(filename)

            #       os.remove(os.path.join(UPLOAD_FOLDER,
            #               examination.path))

            #       file.save(os.path.join(UPLOAD_FOLDER, filename))

            #       examination.path = filename
            #   else:
            #       return render_template('examination/edit.htm',
            #                              courses = courses,
            #       educations = educations, examination=examination,
            #       message = 'Fout file format!');

            db.session.commit()

            flash('Het tentamen is aangepast!', 'success')
            return render_template('examination/edit.htm', courses=courses,
                                   educations=educations,
                                   examination=examination,
                                   message='Het tentamen is aangepast!',
                                   title='Tentamens')

    if request.args.get('edit'):
        exam_id = request.args.get('edit')
        examination = Examination.query.filter(Examination.id == exam_id)\
            .first()

        return render_template('examination/edit.htm', path=path,
                               examination=examination, courses=courses,
                               educations=educations,
                               title='Tentamens')

    examinations = Examination.query.all()
    return render_template('examination/admin.htm', path=path,
                           examinations=examinations, search="",
                           message="Geen examen geselecteerd",
                           title='Tentamens')


@blueprint.route('/course/add', methods=['GET', 'POST'])
def add_course():
    if not GroupPermissionAPI.can_write('examination'):
        session['prev'] = 'examination.add_course'
        return abort(403)

    if request.method == 'POST':
        course = request.form.get("course", None)
        discription = request.form.get("discription", None)
        new_course = Course(course, discription)
        db.session.add(new_course)
        db.session.commit()
        return redirect('../examination/add')

    return render_template('examination/course.htm', title='Tentamens')


@blueprint.route('/education/add', methods=['GET', 'POST'])
def add_education():
    if not GroupPermissionAPI.can_write('examination'):
        session['prev'] = 'examination.add_education'
        return abort(403)

    if request.method == 'POST':
        education = request.form.get("education", None)
        new_education = Education(1, education)

        db.session.add(new_education)
        db.session.commit()
        return redirect('../examination/add')

    return render_template('examination/education.htm', title='Tentamens')


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
    if file:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = create_unique_file(filename)

            if old_path != '1':
                os.remove(os.path.join(UPLOAD_FOLDER, old_path))

            file.save(os.path.join(UPLOAD_FOLDER, filename))

            return filename
        else:
            return False
    else:
        return True
