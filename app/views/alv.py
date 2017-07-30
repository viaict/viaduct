from flask import Blueprint, abort, render_template, request, url_for, redirect
from flask_login import login_required

from app import db
from app.forms.alv import AlvForm
from app.models.alv_model import Alv, AlvPresidium
from app.service import alv_service, user_service
from app.utils.module import ModuleAPI

blueprint = Blueprint('alv', __name__, url_prefix='/alv')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/list/', methods=['GET'])
@login_required
def list():
    if not ModuleAPI.can_read('alv'):
        return abort(403)

    alvs = Alv.query.all()
    return render_template('alv/list.htm', alvs=alvs)


@blueprint.route('/view/<int:alv_id>/', methods=['GET'])
@login_required
def view(alv_id=0):
    if not ModuleAPI.can_read('alv'):
        return abort(403)

    alv = Alv.query.get_or_404(alv_id)
    return render_template('alv/view.htm', alv=alv)


@blueprint.route("/create/", methods=['GET', 'POST'])
@blueprint.route("/edit/<int:alv_id>/", methods=['GET', 'POST'])
@login_required
def create_edit(alv_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    if alv_id:
        alv = alv_service.find_by_id(alv_id) if alv_id else Alv()
    else:
        alv = Alv()

    form = AlvForm.from_alv(request.form, alv)
    print(alv.presidium)
    print(alv.presidium_secretary)

    if form.validate_on_submit():
        alv.en_name = form.en_name.data
        alv.nl_name = form.nl_name.data
        alv.date = form.date.data
        alv.activity = form.activity.data

        if alv.id:
            alv_service.update(alv)
        else:
            alv_service.create(alv)

        def convert_alv_presidium(user, role):
            if not user:
                return None
            return AlvPresidium.from_user_role(user, role)

        chairman = convert_alv_presidium(
            user_service.find_by_id(form.presidium_chairman.data),
            AlvPresidium.CHAIRMAN)
        secretary = convert_alv_presidium(
            user_service.find_by_id(form.presidium_secretary.data),
            AlvPresidium.SECRETARY)
        other = convert_alv_presidium(
            user_service.find_by_id(form.presidium_other.data),
            AlvPresidium.OTHER)
        new_presidium = [u for u in (chairman, secretary, other) if u]
        alv_service.set_alv_presidium(alv, new_presidium)

    return render_template('alv/edit.htm', form=form)


@blueprint.route('/delete/<int:alv_id>/', methods=['POST'])
@login_required
def delete(alv_id=0):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    alv = Alv.query.get_or_404(alv_id)
    db.session.delete(alv)
    db.session.commit()
    return redirect(url_for('alv.list'))
