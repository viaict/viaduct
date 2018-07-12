from flask import Blueprint, render_template, redirect, flash, url_for

from app import db
from app.decorators import require_role
from app.forms import init_form
from app.forms.redirect import RedirectForm
from app.models.redirect import Redirect
from app.roles import Roles

blueprint = Blueprint('redirect', __name__, url_prefix='/redirect')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:redirect_id>/', methods=['GET', 'POST'])
@require_role(Roles.REDIRECT_WRITE)
def view(redirect_id=None):
    redirection = Redirect.query.get(redirect_id) if redirect_id else None

    form = init_form(RedirectForm, obj=redirection)

    if form.validate_on_submit():

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
                           redirection=redirection, form=form)


@blueprint.route('/delete/<int:redirect_id>/', methods=['GET', 'POST'])
@require_role(Roles.REDIRECT_WRITE)
def delete(redirect_id):
    redirection = Redirect.query.get_or_404(redirect_id)

    db.session.delete(redirection)
    db.session.commit()

    flash('De omleiding is succesvol verwijderd.')

    return redirect(url_for('redirect.view'))
