import re

from flask import flash, request, url_for, render_template, redirect, \
    session, jsonify
from flask_babel import _
from flask_login import current_user

from app import app, login_manager
from app.models.page import Page


@login_manager.unauthorized_handler
def unauthorized():
    # Save the path the user was rejected from.
    session['denied_from'] = request.path

    flash(_('You must be logged in to view this page.'), 'danger')
    return redirect(url_for('user.sign_in'))


@app.errorhandler(403)
def permission_denied(e):
    """When permission denied and not logged in you will be redirected."""
    if request.is_xhr:
        return jsonify('You are not allowed to access this resource'), 403

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
    if request.is_xhr:
        return jsonify('An internal server error occurred'), 500
    return render_template('page/500.htm'), 500


@app.errorhandler(404)
def page_not_found(e):
    if request.is_xhr:
        return jsonify('The requested resource could not be found.'), 404

    # Search for file extension.
    if re.match(r'(?:.*)\.[a-zA-Z]{3,}$', request.path):
        return '', 404

    page = Page(request.path.lstrip('/'))
    return render_template('page/404.htm', page=page), 404
