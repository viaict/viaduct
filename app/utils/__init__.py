from flask import flash, Markup

from app import app

from markdown import markdown
import re

from .resource import Resource  # noqa

from .module import import_module  # noqa
from .serialize_sqla import serialize_sqla  # noqa
from .validate_form import validate_form  # noqa

# OLD APIS
from .navigation import NavigationAPI
from .category import CategoryAPI
from .pimpy import PimpyAPI
from .file import FileAPI  # noqa
from .booksales import BookSalesAPI
from .page import PageAPI
from .seo import SeoAPI

from .user import UserAPI
from .module import ModuleAPI

app.jinja_env.globals.update(NavigationAPI=NavigationAPI)
app.jinja_env.globals.update(PimpyAPI=PimpyAPI)
app.jinja_env.globals.update(UserAPI=UserAPI)
app.jinja_env.globals.update(ModuleAPI=ModuleAPI)
app.jinja_env.globals.update(BookSalesAPI=BookSalesAPI)
app.jinja_env.globals.update(PageAPI=PageAPI)
app.jinja_env.globals.update(CategoryAPI=CategoryAPI)
app.jinja_env.globals.update(SeoAPI=SeoAPI)

markdown_extensions = [
    'toc'
]


def flash_form_errors(form):
    for field, errors in list(form.errors.items()):
        for error in errors:
            flash('%s' % error, 'danger')


@app.template_filter('markdown')
def markdown_filter(data, filter_html=True):
    if filter_html:
        safe_mode = False
    else:
        safe_mode = 'escape'

    return Markup(markdown(data, safe_mode=safe_mode, enable_attributes=False,
                           extensions=markdown_extensions))


@app.template_filter('strip_tags')
def strip_tags_filter(data, *args):
    for tag in args:
        # Source: http://stackoverflow.com/a/6445849/849956
        data = re.sub(
            r'<%s(?:\s[^>]*)?(>(?:.(?!/%s>))*</%s>|/>)' % (tag, tag, tag), '',
            data, flags=re.S)

    return data


@app.template_filter('markup')
def markup_filter(data):
    return Markup(data)


@app.template_filter('safe_markdown')
def safe_markdown_filter(data):
    return Markup(markdown(data, extensions=markdown_extensions))


@app.template_filter('pimpy_minute_line_numbers')
def pimpy_minute_line_numbers(data):
    s = ''
    for i, line in enumerate(data.split('\n')):
        s += '<a id="ln%d" class="pimpy_minute_line"/>%s</a>\n' % (i,
                                                                   line[:-1])
    return s
