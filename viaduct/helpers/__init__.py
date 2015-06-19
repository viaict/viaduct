import re

from flask import flash, request, Markup, url_for, render_template, redirect, \
    session
from flask.ext.login import current_user

from markdown import markdown
from .resource import Resource  # noqa

from viaduct import application, login_manager
from viaduct.forms import SignInForm
from viaduct.models import Page

markdown_extensions = [
    'toc'
]


@login_manager.unauthorized_handler
def unauthorized():
    # Save the path the user was rejected from.
    session['denied_from'] = request.path

    flash('You must be logged in to view this page.', 'danger')
    return redirect(url_for('user.sign_in'))


@application.errorhandler(403)
def permission_denied(e):
    """ When permission denied and not logged in you will be redirected. """
    content = "403, The police has been notified!"
    image = '/static/img/403.jpg'

    # Save the path you were rejected from.
    session['denied_from'] = request.path

    if not current_user or current_user.is_anonymous():
        flash('Je hebt geen rechten om deze pagina te bekijken.', 'danger')
        return redirect(url_for('user.sign_in'))

    return render_template('page/403.htm', content=content, image=image), 403


@application.errorhandler(500)
def internal_server_error(e):
    return render_template('page/500.htm'), 500


@application.errorhandler(404)
def page_not_found(e):
    # Search for file extension.
    if re.match(r'(?:.*)\.[a-zA-Z]{3,}$', request.path):
        return '', 404

    page = Page(request.path.lstrip('/'))
    return render_template('page/404.htm', page=page), 404


def flash_form_errors(form):
    for field, errors in list(form.errors.items()):
        for error in errors:
            flash('%s' % error, 'danger')


def get_login_form():
    return SignInForm()


@application.template_filter('markdown')
def markdown_filter(data, filter_html=True):
    if filter_html:
        safe_mode = False
    else:
        safe_mode = 'escape'

    return Markup(markdown(data, safe_mode=safe_mode, enable_attributes=False,
                           extensions=markdown_extensions))


@application.template_filter('strip_tags')
def strip_tags_filter(data, *args):
    for tag in args:
        # Source: http://stackoverflow.com/a/6445849/849956
        data = re.sub(
            r'<%s(?:\s[^>]*)?(>(?:.(?!/%s>))*</%s>|/>)' % (tag, tag, tag), '',
            data, flags=re.S)

    return data


@application.template_filter('markup')
def markup_filter(data):
    return Markup(data)


@application.template_filter('safe_markdown')
def safe_markdown_filter(data):
    return Markup(markdown(data, extensions=markdown_extensions))


@application.template_filter('pimpy_minute_line_numbers')
def pimpy_minute_line_numbers(data):
    s = ''
    for i, line in enumerate(data.split('\n')):
        s += '<a id="ln%d" class="pimpy_minute_line"/>%s</a>\n' % (i,
                                                                   line[:-1])
    return s
