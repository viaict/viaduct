from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, \
    flash
from flask_babel import lazy_gettext as _
from flask_login import current_user
from sqlalchemy import or_, and_

from app import db
from app.decorators import require_role
from app.forms.vacancy import VacancyForm
from app.models.company import Company
from app.models.vacancy import Vacancy
from app.roles import Roles
from app.service import role_service

blueprint = Blueprint('vacancy', __name__, url_prefix='/vacancies')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def list(page_nr=1):

    search = request.args.get('search', None)

    if search:
        vacancies = Vacancy.query.join(Company). \
            filter(or_(Vacancy.title.like('%' + search + '%'),
                       Company.name.like('%' + search + '%'),
                       Vacancy.workload.like('%' + search + '%'),
                       Vacancy.contract_of_service.like(
                           '%' + search + '%')))

        if not role_service.user_has_role(current_user, Roles.VACANCY_WRITE):
            vacancies = vacancies.filter(
                and_(Vacancy.start_date <
                     datetime.utcnow(), Vacancy.end_date >
                     datetime.utcnow()))

        vacancies = vacancies.paginate(page_nr, 15, False)

        can_write = role_service.user_has_role(current_user,
                                               Roles.VACANCY_WRITE)

        return render_template('vacancy/list.htm', vacancies=vacancies,
                               search=search, title="Vacatures",
                               can_write=can_write)

    if role_service.user_has_role(current_user, Roles.VACANCY_WRITE):
        vacancies = Vacancy.query.join(Company)\
                                 .order_by(Vacancy.start_date.desc())
    else:
        res = Vacancy.query.filter(and_(Vacancy.start_date <
                                        datetime.utcnow(), Vacancy.end_date >
                                        datetime.utcnow()))

    res = _order_vacancies(res)

    vacancies = vacancies.paginate(page_nr, 15, False)
    can_write = role_service.user_has_role(current_user, Roles.VACANCY_WRITE)

    return render_template('vacancy/list.htm', vacancies=vacancies,
                           search="", title="Vacatures",
                           can_write=can_write)


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
@require_role(Roles.VACANCY_WRITE)
def edit(vacancy_id=None):
    """Create, view or edit a vacancy."""
    # Select vacancy.
    if vacancy_id:
        vacancy = Vacancy.query.get(vacancy_id)
    else:
        vacancy = Vacancy()

    form = VacancyForm(request.form, obj=vacancy)

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
