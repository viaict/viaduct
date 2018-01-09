import re

from flask import flash, request, url_for, render_template, redirect, \
    session, jsonify
from flask_babel import _
from flask_login import current_user

from app import app, login_manager
from app.exceptions import ResourceNotFoundException, DetailedException
from app.models.page import Page
from app.roles import Roles
from app.service import role_service


@login_manager.unauthorized_handler
def unauthorized():
    # Save the path the user was rejected from.
    session['denied_from'] = request.path

    flash(_('You must be logged in to view this page.'), 'danger')
    return redirect(url_for('user.sign_in'))


def handle_api_error(e):
    return jsonify({"title": e.title,
                    "status": e.status,
                    "detail": str(e),
                    "type": e.type_}), e.status


@app.errorhandler(DetailedException)
def default_detailed_exception_handler(e):
    if request.blueprint.startswith("/api") or request.is_xhr:
        return handle_api_error(e)

    if isinstance(e, ResourceNotFoundException):
        return page_not_found(e)

    return internal_server_error(e)


@app.errorhandler(403)
def permission_denied(e):
    """When permission denied and not logged in you will be redirected."""
    content = "403, The police has been notified!"
    image = '/static/img/403.jpg'

    # Save the path you were rejected from.
    session['denied_from'] = request.path

    if current_user.is_anonymous:
        flash(_('You must be logged in to view this page.'), 'danger')
        return redirect(url_for('user.sign_in'))

    return render_template('page/403.htm', content=content, image=image), 403


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('page/500.htm'), 500


@app.errorhandler(404)
def page_not_found(e):
    # Search for file extension.
    if re.match(r'(?:.*)\.[a-zA-Z]{3,}$', request.path):
        return '', 404

    page = Page(request.path.lstrip('/'))
    can_write = role_service.user_has_role(current_user, Roles.PAGE_WRITE)
    return render_template('page/404.htm', page=page, can_write=can_write), 404
