
from functools import wraps

from flask import Blueprint, render_template, abort, request, redirect, \
    url_for, flash
from viaduct.models.sponsor import Sponsor
from viaduct.forms.sponsor import EditSponsorForm
from viaduct.helpers import flash_form_errors
from viaduct import db
# from flask.ext.login import current_user


blueprint = Blueprint('sponsor', __name__, url_prefix='/sponsors')


def user_allowed(func):
    """
    Wrapper for all public facing views that specifies if a user has access.
    If not an unauthorized response is returned and the requested endpoint
    is never executed.

    TODO: Implement logic for users that are not allowed
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_allowed = True
        if not user_allowed:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper


@blueprint.route('/', methods=['GET'])
@user_allowed
def main():
    """
    Main list view for sponsors
    """
    sponsors = Sponsor.query.order_by('name').all()
    return render_template('sponsor/list.htm',
                           sponsors=sponsors)


def create_or_edit_sponsor(sponsor):
    """
    Given a sponsor the sponsor will be created or updated based on
    the given from data in the post request.
    """
    form = EditSponsorForm(request.form, sponsor)
    if form.validate_on_submit():
        sponsor.name = form.name.data
        db.session.add(sponsor)
        db.session.commit()
        return redirect(url_for('sponsor.main'))
    else:
        flash_form_errors(form)
    return render_template('sponsor/edit.htm', form=form, sponsor=sponsor)


@blueprint.route('/create/', methods=['GET', 'POST'])
@user_allowed
def create():
    """
    Endpoint to create a new sponsor.
    """
    sponsor = Sponsor()
    return create_or_edit_sponsor(sponsor)


@blueprint.route('/edit/<int:sponsor_id>/', methods=['GET', 'POST'])
@user_allowed
def edit(sponsor_id):
    """
    Endpoint to update a sponsor.
    """
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor:
        return create_or_edit_sponsor(sponsor)
    else:
        flash("De opgevraagde sponsor bestaat niet.")
    return redirect(url_for('sponsor.main'))


@blueprint.route('/edit/<int:sponsor_id>/delete/', methods=['POST'])
@user_allowed
def delete(sponsor_id):
    """
    Endpoint to delete a sponsor.
    """
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor:
        db.session.delete(sponsor)
        db.session.commit()
    else:
        flash("De opgevraagde sponsor bestaat niet.")
    return redirect(url_for('sponsor.main'))
