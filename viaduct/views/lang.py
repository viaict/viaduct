#!/usr/bin/env python
# encoding: utf-8

from viaduct import db
from flask import Blueprint, redirect, make_response, request, url_for, flash
from flask.ext.babel import refresh
from flask.ext.login import current_user
from flask.ext.babel import _
from config import LANGUAGES

blueprint = Blueprint('lang', __name__, url_prefix='/lang')


def redirect_url(default='home.home'):
    return request.args.get('next') or request.referrer or url_for(default)


@blueprint.route('/<path:lang>', methods=['GET'])
def set_lang(lang=None):
    if lang not in LANGUAGES.keys():
        flash(_('Language unsupported on this site') + ': ' + lang, 'warning')
        return redirect(url_for('home.home'))

    if current_user.is_anonymous():
        rv = make_response(redirect(redirect_url()))
        rv.set_cookie('lang', lang)
        refresh()
        return rv
    else:
        current_user.locale = lang
        db.session.add(current_user)
        db.session.commit()
        refresh()
        flash(_('Bilingualism is not fully implemented yet!'), 'info')
        return redirect(redirect_url())
