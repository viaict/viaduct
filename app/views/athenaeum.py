"""Embedded website of Athenaeum book sale website."""
from flask import render_template, Blueprint, abort, flash
from flask_babel import _
from flask_login import current_user

blueprint = Blueprint('athenaeum', __name__, url_prefix='/athenaeum')


@blueprint.route('/', methods=['GET'])
def embed():
    if current_user.is_anonymous:
        flash(_('Using the bookstore requires an account.'), 'warning')
        return abort(403)

    """Embed the athenaeum website."""
    url = 'https://mindbus.go2cloud.org/aff_c?offer_id=65&aff_id=501#A-48;36'

    return render_template('athenaeum/embed.htm', url=url)
