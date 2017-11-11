from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, \
    flash
from flask_babel import lazy_gettext as _
from sqlalchemy import or_, and_, func

from app import app, db
from app.decorators import require_role
from app.forms.vacancy import VacancyForm
from app.models.company import Company
from app.models.vacancy import Vacancy
from app.roles import Roles
from app.service import role_service

blueprint = Blueprint('vacancy', __name__, url_prefix='/vacancies')
FILE_FOLDER = app.config['FILE_DIR']


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/<search>/', methods=['GET', 'POST'])
def list(page_nr=1, search=None):
    # Order the vacancies in such a way that vacancies that are new
    # or almost expired, end up on top.
    order = func.abs(
        (100 * (func.datediff(Vacancy.start_date, func.current_date()) /
                func.datediff(Vacancy.start_date, Vacancy.end_date))) - 50)

    if search is not None:
        vacancies = Vacancy.query.join(Company). \
            filter(or_(Vacancy.title.like('%' + search + '%'),
                       Company.name.like('%' + search + '%'),
                       Vacancy.workload.like('%' + search + '%'),
                       Vacancy.contract_of_service.like('%' + search + '%'))) \
            .order_by(order.desc())

        if not role_service.has_role(Roles.VACANCY_WRITE):
            vacancies = vacancies.filter(
                and_(Vacancy.start_date <
                     datetime.utcnow(), Vacancy.end_date >
                     datetime.utcnow()))

        vacancies = vacancies.paginate(page_nr, 15, False)

        return render_template('vacancy/list.htm', vacancies=vacancies,
                               search=search, path=FILE_FOLDER,
                               title="Vacatures")

    if not role_service.has_role(Roles.VACANCY_WRITE):
        vacancies = Vacancy.query.join(Company).order_by(order.desc())
    else:
        vacancies = Vacancy.query.order_by(order.desc()) \
            .filter(and_(Vacancy.start_date <
                         datetime.utcnow(), Vacancy.end_date >
                         datetime.utcnow()))

    vacancies = vacancies.paginate(page_nr, 15, False)

    return render_template('vacancy/list.htm', vacancies=vacancies,
                           search="", path=FILE_FOLDER, title="Vacatures")


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:vacancy_id>/', methods=['GET', 'POST'])
@require_role(Roles.VACANCY_WRITE)
def edit(vacancy_id=None):
    """Create, view or edit a vacancy."""
    # Select vacancy.
    if vacancy_id:
        vacancy = Vacancy.query.get(vacancy_id)
    else:
        vacancy = Vacancy()

    form = VacancyForm(request.form, vacancy)

    # Add companies.
    form.company_id.choices = [(c.id, c.name) for c in Company.query
                               .order_by('name')]

    if form.validate_on_submit():
        if not vacancy.id and Vacancy.query.filter(
                Vacancy.title == form.title.data).count():
            flash(_('Title "%s" is already in use.' % form.title.data),
                  'danger')
            return render_template('vacancy/edit.htm', vacancy=vacancy,
                                   form=form, title="Vacatures")
        vacancy.title = form.title.data
        vacancy.description = form.description.data
        vacancy.start_date = form.start_date.data
        vacancy.end_date = form.end_date.data
        vacancy.contract_of_service = form.contract_of_service.data
        vacancy.workload = form.workload.data
        vacancy.company = Company.query.get(form.company_id.data)

        db.session.add(vacancy)
        db.session.commit()

        if vacancy_id:
            flash(_('Vacancy saved'), 'success')
        else:
            flash(_('Vacancy created'), 'success')
        return redirect(url_for('vacancy.list'))

    return render_template('vacancy/edit.htm', vacancy=vacancy, form=form,
                           title="Vacatures")


@blueprint.route('/delete/<int:vacancy_id>/', methods=['POST'])
@require_role(Roles.VACANCY_WRITE)
def delete(vacancy_id=None):
    """Delete a vacancy."""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    db.session.delete(vacancy)
    db.session.commit()
    flash(_('Vacancy deleted'), 'success')

    return redirect(url_for('vacancy.list'))
