#!/usr/bin/env python
# encoding: utf-8

from flask import Blueprint, redirect, session, url_for, flash
from flask_babel import _
from flask_babel import refresh
from flask_login import current_user

from app import db, app
from app.views import redirect_back

blueprint = Blueprint('lang', __name__, url_prefix='/lang')


@blueprint.route('/set/<path:lang>', methods=['GET'])
def set_user_lang(lang=None):
    if lang not in app.config['LANGUAGES'].keys():
        flash(_('Language unsupported on this site') + ': ' + lang, 'warning')
        return redirect(url_for('home.home'))
    if current_user.is_anonymous:
        flash(_('You need to be logged in to set a permanent language.'))
        return redirect_back()

    current_user.locale = lang
    db.session.add(current_user)
    db.session.commit()
    refresh()
    return redirect_back()


@blueprint.route('/<path:lang>', methods=['GET'])
def set_lang(lang=None):
    if lang not in app.config['LANGUAGES'].keys():
        flash(_('Language unsupported on this site') + ': ' + lang, 'warning')
        return redirect(url_for('home.home'))

    session['lang'] = lang
    if current_user.is_authenticated:
        msg = _("{} is now set as language for this session. To make this "
                "setting permanent, <a href='{}'>click here</a>")
        flash(msg.format(app.config['LANGUAGES'][lang],
                         url_for('lang.set_user_lang', lang=lang)),
              'safe')

    return redirect_back()
