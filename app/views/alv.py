from flask import Blueprint, abort, render_template, request, url_for, redirect
from flask_login import login_required

from app import db
from app.forms.alv import AlvForm
from app.utils.module import ModuleAPI
from app.models.alv import Alv  # , AlvPresidium

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
def edit(alv_id=0):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    alv = Alv.query.get_or_404(alv_id) if alv_id else Alv()
    form = AlvForm(request.form)

    # presidium = AlvPresidium.query.filter(AlvPresidium.alv == alv).all()

    if form.validate_on_submit():
        form.populate_obj(alv)

        db.session.add(alv)
        db.session.commit()

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
