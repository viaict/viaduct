from flask import Blueprint, render_template, request, abort, redirect, \
    flash, url_for
from app import db
from app.models import Redirect
from app.forms import RedirectForm
from app.api.module import ModuleAPI

blueprint = Blueprint('redirect', __name__, url_prefix='/redirect')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:redirect_id>/', methods=['GET', 'POST'])
def view(redirect_id=None):
    if not ModuleAPI.can_read('redirect'):
        return abort(403)

    can_write = ModuleAPI.can_write('redirect')

    redirection = Redirect.query.get(redirect_id) if redirect_id else None

    if redirection:
        form = RedirectForm(request.form, redirection)
    else:
        form = RedirectForm(request.form)

    if form.validate_on_submit():
        if not can_write:
            return abort(403)

        fro = form.data['fro'].rstrip('/')
        to = form.data['to']

        old_redirection = Redirect.query.filter(Redirect.fro == fro).first()

        if old_redirection and old_redirection.id != redirect_id:
            flash('Er is al een omleiding vanaf dat pad gedefiniëerd.',
                  'danger')
        else:
            if redirection:
                redirection.fro = fro
                redirection.to = to
            else:
                redirection = Redirect(fro, to)

            db.session.add(redirection)
            db.session.commit()

            flash('De omleiding is succesvol opgeslagen.')

            return redirect(url_for('redirect.view',
                                    redirect_id=redirection.id))

    redirections = Redirect.query.order_by(Redirect.fro).all()

    return render_template('redirect.htm', redirections=redirections,
                           redirection=redirection, form=form,
                           can_write=can_write)


@blueprint.route('/delete/<int:redirect_id>/', methods=['GET', 'POST'])
def delete(redirect_id):
    if not ModuleAPI.can_write('redirect'):
        return abort(403)

    redirection = Redirect.query.get(redirect_id)

    if not redirection:
        return abort(404)

    db.session.delete(redirection)
    db.session.commit()

    flash('De omleiding is succesvol verwijderd.')

    return redirect(url_for('redirect.view'))
