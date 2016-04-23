from flask import Blueprint
from flask import flash, redirect, render_template, url_for
from flask.ext.login import login_required
from flask.ext.babel import _

from app import app

import requests
import datetime as dt

DOMJUDGE_URL = app.config['DOMJUDGE_URL']
DT_FORMAT = app.config['DT_FORMAT']

blueprint = Blueprint('domjudge', __name__, url_prefix='/domjudge')


def flash_error():
    flash(_("Request to DOMjudge server failed"), 'danger')


def domjudge_request_get(url):
    try:
        r = requests.get(DOMJUDGE_URL + url, timeout=(5, 5))
    except:
        flash_error()
        return None

    if r.status_code != 200:
        flash_error()
        return None

    return r


@blueprint.route('/')
def contest_list():
    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/list.htm')

    data = list(r.json().values())
    for c in data:
        c['start'] = dt.datetime.fromtimestamp(c['start']) \
            .strftime(DT_FORMAT)
        c['end'] = dt.datetime.fromtimestamp(c['end']).strftime(DT_FORMAT)

    data.sort(key=lambda x: x['name'])
    return render_template('domjudge/list.htm', contests=data)


@blueprint.route('/contest/<int:contest_id>/')
def contest_view(contest_id=None):
    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/view.htm')

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist"), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]
    contest['start'] = dt.datetime.fromtimestamp(contest['start']) \
        .strftime(DT_FORMAT)
    contest['end'] = dt.datetime.fromtimestamp(contest['end']) \
        .strftime(DT_FORMAT)

    r = domjudge_request_get('api/scoreboard?cid={}'.format(contest_id))

    if not r:
        return render_template('domjudge/view.htm')
    scoreboard = r.json()
    for team in scoreboard:
        for problem in team['problems']:
            # TODO: find out what exactly 'solved first' means
            if problem['solved']:
                _class = "domjudge-problem-solved-cell"
            else:
                if problem['num_judged'] > 0:
                    _class = "domjudge-problem-incorrect-cell"
                else:
                    _class = "domjudge-problem-untried-cell"

            problem['class'] = _class

        team['problems'].sort(key=lambda x: x['label'])

    r = domjudge_request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/view.htm')
    problems = r.json()
    problems.sort(key=lambda x: x['label'])

    r = domjudge_request_get('api/teams')
    if not r:
        return render_template('domjudge/view.htm')

    teams = r.json()
    teams_dict = {}
    for team in teams:
        teams_dict[team['id']] = team

    return render_template('domjudge/view.htm',
                           contest=contest, scoreboard=scoreboard,
                           problems=problems, teams=teams_dict)


@blueprint.route('/contest/<int:contest_id>/submit/')
@login_required
def contest_submit(contest_id=None):
    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/list.htm')
