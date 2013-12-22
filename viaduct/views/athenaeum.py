"""Embedded website of Athenaeum book sale website."""
from flask import render_template, Blueprint

blueprint = Blueprint('athenaeum', __name__, url_prefix='/athenaeum')


@blueprint.route('/', methods=['GET'])
def embed():
    """Embed the athenaeum website."""
    url = 'http://athenaeum-sv.mijnboekhandelaar.com/'

    return render_template('athenaeum/embed.htm', url=url)
