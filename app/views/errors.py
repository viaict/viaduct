import re
import werkzeug.exceptions
from connexion.apis.flask_api import FlaskApi
from connexion.exceptions import ProblemException
from connexion.problem import problem
from flask import flash, request, url_for, render_template, redirect, \
    session, jsonify
from flask_babel import _
from flask_login import current_user
from functools import wraps

from app import app, login_manager
from app.exceptions.base import ResourceNotFoundException, \
    ApplicationException, AuthorizationException
from app.models.page import Page
from app.roles import Roles
from app.service import role_service


@login_manager.unauthorized_handler
def unauthorized():
    # Save the path the user was rejected from.
    session['denied_from'] = request.path

    flash(_('You must be logged in to view this page.'), 'danger')
    return redirect(url_for('user.sign_in'))


def add_api_error_handler(f):
    @wraps(f)
    def wrapper(e):
        if request.path.startswith('/api') or request.is_xhr:
            return handle_api_error(e)

        return f(e)

    return wrapper


def handle_api_error(e):
    if isinstance(e, ApplicationException):
        return jsonify({"title": e.title,
                        "status": e.status,
                        "detail": str(e),
                        "type": e.type_}), e.status

    if not isinstance(e, werkzeug.exceptions.HTTPException):
        e = werkzeug.exceptions.InternalServerError()

    response = problem(title=e.name,
                       detail=e.description,
                       status=e.code)

    return FlaskApi.get_response(response)


@app.errorhandler(ProblemException)
def connexion_problem_exception_handler(e):
    return FlaskApi.get_response(e.to_problem())


@app.errorhandler(ApplicationException)
@add_api_error_handler
def default_detailed_exception_handler(e):
    if isinstance(e, ResourceNotFoundException):
        return page_not_found(e)
    if isinstance(e, AuthorizationException):
        return permission_denied(e)

    return internal_server_error(e)


@app.errorhandler(401)
@app.errorhandler(403)
@add_api_error_handler
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
@add_api_error_handler
def internal_server_error(_):
    return render_template('page/500.htm'), 500


@app.errorhandler(404)
@add_api_error_handler
def page_not_found(_):
    # Search for file extension.
    if re.match(r'(?:.*)\.[a-zA-Z]{2,}$', request.path):
        return '', 404

    page = Page(request.path.lstrip('/'))
    can_write = role_service.user_has_role(current_user, Roles.PAGE_WRITE)
    return render_template('page/404.htm', page=page, can_write=can_write), 404
