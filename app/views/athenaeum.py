"""Embedded website of Athenaeum book sale website."""
from flask import render_template, Blueprint, abort, flash, make_response
from flask_babel import _
from flask_login import current_user
from app.service import pdf_service

blueprint = Blueprint('athenaeum', __name__, url_prefix='/athenaeum')


@blueprint.route('/discount-card', methods=['GET'])
def generate_pdf():
    if not current_user.has_paid:
        flash(_('You need to be member of via to obtain a discount card.'),
              'warning')
        return abort(403)

    pdf_string = pdf_service.user_discount_card(current_user.id)

    filename = "discountcard_{0}.pdf".format(current_user.student_id)

    response = make_response(pdf_string)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename = %s' % filename

    return response


@blueprint.route('/', methods=['GET'])
def embed():
    if current_user.is_anonymous:
        flash(_('Using the bookstore requires an account.'), 'warning')
        return abort(403)

    """Embed the athenaeum website."""
    url = 'https://www.athenaeum.nl/studieboeken/studieverenigingen/#A-12;10'

    return render_template('athenaeum/embed.htm', url=url)
