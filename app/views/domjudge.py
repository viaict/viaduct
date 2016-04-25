from flask import Blueprint
from flask import flash, redirect, \
    render_template, url_for, request, Response
from flask.ext.login import login_required
from flask.ext.babel import _

from app import app
from flask.ext.login import current_user
from app.models.user import User

import requests
import datetime as dt
import re

DOMJUDGE_URL = app.config['DOMJUDGE_URL']
DOMJUDGE_ADMIN_USERNAME = app.config['DOMJUDGE_ADMIN_USERNAME']
DOMJUDGE_ADMIN_PASSWORD = app.config['DOMJUDGE_ADMIN_PASSWORD']

DT_FORMAT = app.config['DT_FORMAT']
VIA_USER_TEAM = re.compile(r"^via_user_team_(\d+)$")

blueprint = Blueprint('domjudge', __name__, url_prefix='/domjudge')


def flash_error():
    flash(_("Request to DOMjudge server failed"), 'danger')


def domjudge_request_get(url, session=None):
    if not session:
        session = requests
    try:
        r = session.get(DOMJUDGE_URL + url, timeout=(5, 5))
    except:
        flash_error()
        return None

    if r.status_code != 200:
        flash_error()
        return None

    return r


def domjudge_request_post(url, data, files={},
                          session=None, flash_on_error=True):
    if not session:
        session = requests.Session()
    try:
        r = session.post(DOMJUDGE_URL + url, data=data,
                         files=files, timeout=(5, 5))
    except Exception as e:
        if flash_on_error:
            flash_error()
        return (False, e, session)

    if r.status_code >= 400:
        if flash_on_error:
            flash_error()
        return (False, r, session)

    return (True, r, session)


def domjudge_login(username, password, flash_on_error=True):
    form_data = {
        'cmd': 'login',
        'login': username,
        'passwd': password
    }

    (result, _, session) = domjudge_request_post('public/login.php', form_data,
                                                 flash_on_error=flash_on_error)
    if result:
        return session
    return None


def domjudge_logout(session):
    domjudge_request_get('auth/logout.php', session=session)


def domjudge_add_user(username, password, full_name, email, teamid, session):
    form_data = {
        'data[0][username]': username,
        'data[0][name]': full_name,
        'data[0][email]': email,
        'data[0][password]': password,
        'data[0][enabled]': 1,
        'data[0][teamid]': teamid,
        'data[0][mapping][0][items][2]': 3,  # team role has id 3
        'data[0][mapping][0][fk][0]': 'userid',
        'data[0][mapping][0][fk][1]': 'roleid',
        'data[0][mapping][0][table]': 'userrole',
        'cmd': 'add',
        'table': 'user'
    }

    (result, r, _) = domjudge_request_post(
        'jury/edit.php', form_data, session=session)

    if result:
        return r
    return None


def domjudge_add_team(name, member, categoryid, session):
    form_data = {
        'data[0][name]': name,
        'data[0][members]': member,
        'data[0][categoryid]': categoryid,
        'data[0][comments]': 'Created by Viaduct on {}'.format(
            dt.datetime.now().strftime(DT_FORMAT)),
        'data[0][enabled]': '1',
        'table': 'team',
        'cmd': 'add'
    }

    (result, r, _) = domjudge_request_post(
        'jury/edit.php', form_data, session=session)

    if result:
        return r
    return None


def domjudge_get_viaduct_category_id(session):
    r = domjudge_request_get("api/categories", session=session)
    if not r:
        return None

    for category in r.json():
        if category['name'] == 'viaduct_user':
            return category['categoryid']

    return None


def domjudge_get_teamid_for_user(name, viaduct_user_cat_id, session):
    r = domjudge_request_get('api/teams?category={}'.format(
        viaduct_user_cat_id), session=session)
    if not r:
        return None
    for team in r.json():
        if team['name'] == name:
            return team['id']

    return None


def domjudge_submit(contest_shortname, language_id, problem_shortname,
                    file, session):
    form_data = {
        'shortname': problem_shortname,
        'langid': language_id,
        'contest': contest_shortname,
    }
    filename = file.filename
    content = file.read()
    files = {
        'code[]': (filename, content)
    }
    (result, r, _) = domjudge_request_post('api/submissions', form_data,
                                           files=files, session=session)
    if result:
        return r
    else:
        assert(False)


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
    fullscreen = 'fullscreen' in request.args

    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/view.htm', fullscreen=fullscreen)

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
        return render_template('domjudge/view.htm', fullscreen=fullscreen)

    teams = r.json()
    teams_dict = {}
    for team in teams:
        m = VIA_USER_TEAM.match(team['name'])
        if m:
            user_id = int(m.group(1))
            user = User.query.get(user_id)
            team['name'] = '{} {}'.format(user.first_name, user.last_name)

        teams_dict[team['id']] = team

    return render_template('domjudge/view.htm', fullscreen=fullscreen,
                           contest=contest, scoreboard=scoreboard,
                           problems=problems, teams=teams_dict)


@blueprint.route('/contest/<int:contest_id>/problems/')
def contest_problems_list(contest_id):
    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/problem/list.htm')

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist"), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]
    contest['start'] = dt.datetime.fromtimestamp(contest['start']) \
        .strftime(DT_FORMAT)
    contest['end'] = dt.datetime.fromtimestamp(contest['end']) \
        .strftime(DT_FORMAT)

    r = domjudge_request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/problem/list.htm')

    problems = r.json()
    problems.sort(key=lambda x: x['label'])

    return render_template('domjudge/problem/list.htm',
                           contest=contest, problems=problems)


@blueprint.route('/problem/<int:problem_id>/')
def contest_problem_view(problem_id):
    r = domjudge_request_get('public/problem.php?id={}'.format(problem_id))
    if not r:
        return redirect(url_for('domjudge.contest_list'))

    return Response(r.content, mimetype=r.headers['Content-Type'])


@blueprint.route('/contest/<int:contest_id>/problem/<int:problem_id>/submit/',
                 methods=['GET', 'POST'])
@login_required
def contest_problem_submit(contest_id, problem_id):
    r = domjudge_request_get('api/languages')
    if not r:
        return render_template('domjudge/problem/submit.htm',
                               contest_id=contest_id)

    languages = r.json()

    r = domjudge_request_get('api/contests')
    if not r:
        return render_template('domjudge/problem/submit.htm',
                               contest_id=contest_id)

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist."), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]
    contest['start'] = dt.datetime.fromtimestamp(contest['start']) \
        .strftime(DT_FORMAT)
    contest['end'] = dt.datetime.fromtimestamp(contest['end']) \
        .strftime(DT_FORMAT)

    r = domjudge_request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/problem/submit.htm',
                               contest_id=contest_id)

    problem = None
    for p in r.json():
        if p['id'] == problem_id:
            problem = p
            break

    if not problem:
        flash(_('Problem does not exist.'), 'danger')
        return redirect(url_for('domjudge.contest_problems_list',
                                contest_id=contest_id))

    if request.method == 'POST':
        file = request.files.get('file', None)
        language = request.form.get('language', None)

        error = False
        if not file or file.filename == '':
            flash(_('No file uploaded.'), 'danger')
            error = True

        if not language:
            flash(_('Invalid language.'), 'danger')
            error = True
        else:
            valid = False
            for lang in languages:
                if lang['id'] == language:
                    valid = True
                    break

            if not valid:
                flash(_('Invalid language.'), 'danger')
                error = True

        if error:
            return render_template('domjudge/problem/submit.htm',
                                   problem=problem,
                                   contest=contest,
                                   contest_id=contest_id,
                                   languages=languages)

        dom_username = "via_user_{}".format(current_user.id)
        dom_teamname = 'via_user_team_{}'.format(current_user.id)
        dom_password = current_user.password
        session = domjudge_login(dom_username, dom_password,
                                 flash_on_error=False)

        # Check if user exists
        if not session:
            # User does not exist
            session = domjudge_login(DOMJUDGE_ADMIN_USERNAME,
                                     DOMJUDGE_ADMIN_PASSWORD)

            # Admin login failed, just give a 'request failed' error flash
            if not session:
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            # Get the id of the 'viaduct_user' team category
            viaduct_user_cat_id = domjudge_get_viaduct_category_id(session)
            if not viaduct_user_cat_id:
                flash('Team category viaduct_user not found on DOMjudge.',
                      'danger')
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            # Check if the team already exists. This should normally
            # not be the case, but things can go wrong if we
            # create a new team anyway, since team names are not unique.
            user_team_id = domjudge_get_teamid_for_user(dom_teamname,
                                                        viaduct_user_cat_id,
                                                        session)
            if not user_team_id:
                r = domjudge_add_team(dom_teamname, dom_username,
                                      viaduct_user_cat_id, session)
                if not r:
                    return render_template('domjudge/problem/submit.htm',
                                           contest_id=contest_id)

                # Get the id of the newly created team
                user_team_id = domjudge_get_teamid_for_user(
                    dom_teamname, viaduct_user_cat_id, session)

            # Create the user
            r = domjudge_add_user(
                dom_username, dom_password,
                current_user.first_name + " " + current_user.last_name,
                current_user.email, user_team_id, session)

            if not r:
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            domjudge_logout(session)

            # Login as the new user
            session = domjudge_login(dom_username, dom_password)

            if not session:
                return render_template('domjudge/problem/submit.htm')

        r = domjudge_submit(contest['shortname'], language,
                            problem['shortname'], file, session)
        if not r:
            return render_template('domjudge/problem/submit.htm',
                                   contest_id=contest_id)
        flash(_("Submission successful."))
        return redirect(url_for('domjudge.contest_view',
                                contest_id=contest_id))
    else:
        return render_template('domjudge/problem/submit.htm',
                               problem=problem,
                               contest=contest,
                               contest_id=contest_id,
                               languages=languages)
