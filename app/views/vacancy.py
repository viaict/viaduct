from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, \
    abort, flash
from flask_babel import lazy_gettext as _
from flask_sqlalchemy import Pagination
from sqlalchemy import or_, and_

from app import app, db
from app.models.vacancy import Vacancy
from app.models.company import Company
from app.forms import VacancyForm
from app.utils.module import ModuleAPI

blueprint = Blueprint('vacancy', __name__, url_prefix='/vacancies')
FILE_FOLDER = app.config['FILE_DIR']


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/<search>/', methods=['GET', 'POST'])
def list(page_nr=1, search=None):
    if search is not None:
        vacancies = Vacancy.query.join(Company). \
            filter(or_(Vacancy.title.like('%' + search + '%'),
                       Company.name.like('%' + search + '%'),
                       Vacancy.workload.like('%' + search + '%'),
                       Vacancy.contract_of_service.like(
                           '%' + search + '%')))

        if not ModuleAPI.can_write('vacancy'):
            vacancies = vacancies.filter(
                and_(Vacancy.start_date <
                     datetime.utcnow(), Vacancy.end_date >
                     datetime.utcnow()))

        vacancies = vacancies.paginate(page_nr, 15, False)

        return render_template('vacancy/list.htm', vacancies=vacancies,
                               search=search, path=FILE_FOLDER,
                               title="Vacatures")

    if ModuleAPI.can_write('vacancy'):
        res = Vacancy.query.join(Company)
    else:
        res = Vacancy.query.filter(and_(Vacancy.start_date <
                                        datetime.utcnow(), Vacancy.end_date >
                                        datetime.utcnow()))

    res = _order_vacancies(res)

    if page_nr is None:
        try:
            page_nr = int(request.args.get('page', 1))
        except (TypeError, ValueError):
            abort(404)

    index = (page_nr - 1) * 15

    vacancies = Pagination(None, page_nr, 15, len(res), res[index:index + 15])

    return render_template('vacancy/list.htm', vacancies=vacancies,
                           search="", path=FILE_FOLDER, title="Vacatures")


def _order_vacancies(vacancies):
    # Order the vacancies in such a way that vacancies that are new
    # or almost expired, end up on top.
    def key(vacancy):
        old = (vacancy.start_date - datetime.now().date()).days
        new = (vacancy.start_date - vacancy.end_date).days

        return abs((100 * (old / min(1, 1 if new == 0 else new)) - 50))

    return sorted(vacancies, key=key, reverse=True)


@blueprint.route('/create/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:vacancy_id>/', methods=['GET', 'POST'])
def edit(vacancy_id=None):
    """Create, view or edit a vacancy."""
    if not ModuleAPI.can_write('vacancy'):
        return abort(403)

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
def delete(vacancy_id=None):
    """Delete a vacancy."""
    if not ModuleAPI.can_write('vacancy'):
        return abort(403)

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    db.session.delete(vacancy)
    db.session.commit()
    flash(_('Vacancy deleted'), 'success')

    return redirect(url_for('vacancy.list'))
