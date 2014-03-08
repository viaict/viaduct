from flask import Blueprint

from viaduct import db
from viaduct.models import Page, NewsRevision
import viaduct.api.news as NewsAPI

blueprint = Blueprint('news', __name__)


@blueprint.route('/edit/news/<int:item_id>/', methods=['GET', 'POST'])
def edit_news(item_id):
    page = NewsAPI.get_page(item_id)
    print(page)

    return ''
