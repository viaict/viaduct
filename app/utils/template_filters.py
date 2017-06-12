from flask import Markup

from app import app

from markdown import markdown
import re


markdown_extensions = [
    'toc'
]


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


@app.template_filter('strip_attrs')
def strip_attrs_filter(data, *args):
    for tag in args:
        # Source: http://stackoverflow.com/a/6445849/849956
        data = re.sub(
            r'(%s=")([a-zA-Z0-9:;\.\s\(\)\-\,#]*)(")' % tag, '',
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
