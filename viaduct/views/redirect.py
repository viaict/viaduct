from flask import Blueprint, render_template, request, abort, redirect, \
    flash, url_for
from viaduct import db
from viaduct.models import Redirect
from viaduct.forms import RedirectForm
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('redirect', __name__, url_prefix='/redirect')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:redirect_id>/', methods=['GET', 'POST'])
def view(redirect_id=None):
    if not GroupPermissionAPI.can_read('redirect'):
        return abort(403)

    can_write = GroupPermissionAPI.can_write('redirect')

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
            flash('A redirect from that path is already defined.', 'danger')
        else:
            if redirection:
                redirection.fro = fro
                redirection.to = to
            else:
                redirection = Redirect(fro, to)

            db.session.add(redirection)
            db.session.commit()

            flash('The redirect has been saved succesfully.')

            return redirect(url_for('redirect.view',
                                    redirect_id=redirection.id))

    redirections = Redirect.query.order_by(Redirect.fro).all()

    return render_template('redirect.htm', redirections=redirections,
                           redirection=redirection, form=form,
                           can_write=can_write)


@blueprint.route('/delete/<int:redirect_id>/', methods=['GET', 'POST'])
def delete(redirect_id):
    if not GroupPermissionAPI.can_write('redirect'):
        return abort(403)

    redirection = Redirect.query.get(redirect_id)

    if not redirection:
        return abort(404)

    db.session.delete(redirection)
    db.session.commit()

    flash('The redirect has been deleted succesfully.')

    return redirect(url_for('redirect.view'))
