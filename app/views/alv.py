from flask import Blueprint, abort, render_template, request, url_for, redirect
from flask_login import login_required

from app import db
from app.forms.alv import AlvForm
from app.models.alv_model import Alv
from app.service import alv_service
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
    if alv_id:
        alv = alv_service.get_by_id(alv_id)

    return render_template('alv/view.htm', alv=alv)


@blueprint.route("/create/", methods=['GET', 'POST'])
@blueprint.route("/edit/<int:alv_id>/", methods=['GET', 'POST'])
@login_required
def create_edit(alv_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    if alv_id:
        alv = alv_service.get_by_id(alv_id)
    else:
        alv = Alv()

    form = AlvForm(request.form, alv)

    if form.validate_on_submit():
        form.populate_obj(alv)
        alv_service.save(alv)
        return redirect(url_for('alv.list'))

    return render_template('alv/edit.htm', form=form)


@blueprint.route('/delete/<int:alv_id>/', methods=['POST'])
@login_required
def delete(alv_id=0):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    if alv_id:
        alv = alv_service.find_by_id(alv_id)

    db.session.delete(alv)
    db.session.commit()

    return redirect(url_for('alv.list'))
