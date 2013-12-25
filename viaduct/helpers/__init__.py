from flask import flash, request, Markup, url_for, render_template, redirect, \
    session
from flask.ext.login import current_user


from viaduct import application, login_manager
from markdown import markdown
from resource import Resource
from viaduct.api.user import UserAPI
from viaduct.api.group import GroupPermissionAPI

from viaduct.models.activity import Activity

import datetime

markdown_extensions = [
    'toc'
]


@login_manager.unauthorized_handler
def unauthorized():
    # Save the path the user was rejected from.
    session['denied_from'] = request.path

    flash('You must be logged in to view this page.', 'error')
    return redirect(url_for('user.sign_in'))


@application.errorhandler(403)
def permission_denied(e):
    """ When permission denied and not logged in you will be redirected. """
    content = "403, The police has been notified!"
    image = '/static/img/403.jpg'

    # Save the path you were rejected from.
    session['denied_from'] = request.path

    if not current_user or current_user.is_anonymous():
        flash('Je hebt geen rechten om deze pagina te bekijken.')
        return redirect(url_for('user.sign_in'))

    return render_template('page/403.htm', content=content, image=image)


@application.errorhandler(500)
def internal_server_error(e):
    return render_template('page/500.htm')


@application.errorhandler(404)
def page_not_found(e):
    return render_template('page/404.htm')


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')


@application.template_filter('markdown')
def markdown_filter(data):
    return Markup(markdown(data, safe_mode='escape', enable_attributes=False,
                           extensions=markdown_extensions))


@application.template_filter('safe_markdown')
def safe_markdown_filter(data):
    return Markup(markdown(data, extensions=markdown_extensions))


@application.template_filter('pages')
def pages_filter(data):

    content = '<div class="container">'

    for i in range(len(data)):
        if i % 2 == 0:
            content += '<div class="row">'

        if i == len(data) - 1 and i % 2 == 0:
            content += '<div class="span10">'
        else:
            content += '<div class="span6">'

        content += '<div class="mainblock'
        # expander toevoegen als het over de mainpage gaat
        content += ' expander">' if data[i].is_main_page else '">'

        page = data[i].page if data[i].page.id else None
        if (page and current_user and (UserAPI.can_write(page) or
                                       GroupPermissionAPI.can_write('page')))\
                or (not page and GroupPermissionAPI.can_write('page')):
            content += '<div class="btn-group">'
            content += '<a class="btn" href="' +\
                url_for('page.get_page_history', path=data[i].path) +\
                '"><i class="icon-time"></i> View History</a>'
            content += '<a class="btn" href="' +\
                url_for('page.edit_page', path=data[i].path) +\
                '"><i class="icon-pencil"></i> Edit Page</a>'
            content += '</div>'

        # if we render stuff for the main page we want to make sure
        # the individual pages are rendered correctly, this is super
        # hard coded but, well, what can you do?
        if data[i].is_main_page:
            if data[i].path == 'twitter':
                content += '<h1>{0}</h1>'.format(data[i].title)
                content += markdown(data[i].content, enable_attributes=False,
                                    extensions=markdown_extensions)
            elif data[i].path == 'activities':
                activities = Activity.query \
                    .filter(Activity.end_time > datetime.datetime.now()) \
                    .order_by(Activity.start_time.asc())
                content += render_template('activity/view_simple.htm',
                                           activities=activities
                                           .paginate(1, 12, False))
            elif data[i].path == 'contact'\
                    or data[i].path == 'laatste_bestuursblog':
                content += '<h1>{0}</h1>'.format(data[i].title)
                content += markdown(data[i].content,
                                    extensions=markdown_extensions)
        else:
            #print data[i].path
            content += '<h1>{0}</h1>'.format(data[i].title)
            content += '<h2>Hello</h2>'
            content += markdown(data[i].content,
                                extensions=markdown_extensions)

        content += '</div></div>'

        if i == len(data) - 1 or i % 2 != 0:
            content += '</div>'

    content += '</div>'

    return Markup(content)
