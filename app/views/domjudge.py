from flask import Blueprint
from flask import flash, redirect, \
    render_template, url_for, request, Response, abort
from flask.ext.login import login_required
from flask.ext.babel import _

from app import app
from flask.ext.login import current_user
from app.models.user import User

from app.utils.domjudge import DOMjudgeAPI

import datetime as dt
import re
import math


DOMJUDGE_URL = app.config['DOMJUDGE_URL']
DOMJUDGE_ADMIN_USERNAME = app.config['DOMJUDGE_ADMIN_USERNAME']
DOMJUDGE_ADMIN_PASSWORD = app.config['DOMJUDGE_ADMIN_PASSWORD']

DT_FORMAT = app.config['DT_FORMAT']
VIA_USER_TEAM = re.compile(r"^via_user_team_(\d+)$")


blueprint = Blueprint('domjudge', __name__, url_prefix='/domjudge')


def get_teams():
    r = DOMjudgeAPI.request_get('api/teams')
    if not r:
        return None

    teams = r.json()
    teams_dict = {}
    for team in teams:
        origname = team['name']
        m = VIA_USER_TEAM.match(origname)
        if m:
            user_id = int(m.group(1))
            user = User.query.get(user_id)
            if user:
                team['name'] = '{} {}'.format(user.first_name, user.last_name)

        team['origname'] = origname
        teams_dict[team['id']] = team

    return teams_dict


@blueprint.route('/')
def contest_list():
    r = DOMjudgeAPI.request_get('api/contests')
    if not r:
        return render_template('domjudge/list.htm')

    data = list(r.json().values())
    for c in data:
        c['start'] = dt.datetime.fromtimestamp(c['start']) \
            .strftime(DT_FORMAT)
        c['end'] = dt.datetime.fromtimestamp(c['end']).strftime(DT_FORMAT)

    data.sort(key=lambda x: x['name'])
    return render_template('domjudge/list.htm', contests=data)


@blueprint.route('/contest/<int:contest_id>/', defaults={'page': 1})
@blueprint.route('/contest/<int:contest_id>/<int:page>')
def contest_view(contest_id, page):
    fullscreen = 'fullscreen' in request.args
    embed = 'embed' in request.args

    r = DOMjudgeAPI.request_get('api/contests')
    if not r:
        return render_template('domjudge/view.htm', fullscreen=fullscreen)

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist."), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]
    contest['start'] = dt.datetime.fromtimestamp(contest['start']) \
        .strftime(DT_FORMAT)
    contest['end'] = dt.datetime.fromtimestamp(contest['end']) \
        .strftime(DT_FORMAT)

    r = DOMjudgeAPI.request_get('api/scoreboard?cid={}'.format(contest_id))

    if not r:
        return render_template('domjudge/view.htm')
    scoreboard = r.json()

    r = DOMjudgeAPI.request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/view.htm')
    problems = r.json()
    problems.sort(key=lambda x: x['label'])

    problems_per_page = 8
    use_pagination = len(problems) > problems_per_page
    if use_pagination:
        amount_pages = math.ceil(len(problems) / problems_per_page)
        problems = problems[(page - 1) * problems_per_page:
                            page * problems_per_page]
    else:
        amount_pages = 1

    if page > amount_pages:
        return abort(404)

    problems_first = {}
    for team in scoreboard:
        team['problems'].sort(key=lambda x: x['label'])
        if use_pagination:
            team['problems'] = team['problems'][(page - 1) * problems_per_page:
                                                page * problems_per_page]
        for problem in team['problems']:
            if problem['solved']:
                _class = "domjudge-problem-solved-cell"
                problem_label = problem['label']
                if problem_label in problems_first:
                    (p, besttime) = problems_first[problem_label]
                    if problem['time'] < besttime:
                        problems_first[problem_label] = \
                            (problem, problem['time'])
                else:
                    problems_first[problem_label] = \
                        (problem, problem['time'])
            else:
                if problem['num_judged'] > 0:
                    _class = "domjudge-problem-incorrect-cell"
                else:
                    _class = "domjudge-problem-untried-cell"

            problem['class'] = _class

    for (problem, time) in problems_first.values():
        problem['class'] = 'domjudge-problem-solved-first-cell'

    teams_dict = get_teams()
    if teams_dict is None:
        return render_template('domjudge/view.htm', fullscreen=fullscreen)

    return render_template('domjudge/view.htm', teams=teams_dict, **locals())


@blueprint.route('/contest/<int:contest_id>/problems/')
def contest_problems_list(contest_id):
    r = DOMjudgeAPI.request_get('api/contests')
    if not r:
        return render_template('domjudge/problem/list.htm')

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist."), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]
    contest['start'] = dt.datetime.fromtimestamp(contest['start']) \
        .strftime(DT_FORMAT)
    contest['end'] = dt.datetime.fromtimestamp(contest['end']) \
        .strftime(DT_FORMAT)

    r = DOMjudgeAPI.request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/problem/list.htm')

    problems = r.json()
    problems.sort(key=lambda x: x['label'])

    return render_template('domjudge/problem/list.htm',
                           contest=contest, problems=problems)


@blueprint.route('/problem/<int:problem_id>/')
def contest_problem_view(problem_id):
    r = DOMjudgeAPI.request_get('public/problem.php?id={}'.format(problem_id))
    if not r:
        return redirect(url_for('domjudge.contest_list'))

    return Response(r.content, mimetype=r.headers['Content-Type'])


@blueprint.route('/contest/<int:contest_id>/problem/<int:problem_id>/submit/',
                 methods=['GET', 'POST'])
@login_required
def contest_problem_submit(contest_id, problem_id):
    r = DOMjudgeAPI.request_get('api/languages')
    if not r:
        return render_template('domjudge/problem/submit.htm',
                               contest_id=contest_id)

    languages = r.json()

    r = DOMjudgeAPI.request_get('api/contests')
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

    r = DOMjudgeAPI.request_get('api/problems?cid={}'.format(contest_id))
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
        session = DOMjudgeAPI.login(dom_username, dom_password,
                                    flash_on_error=False)

        # Check if user exists
        if not session:
            # User does not exist
            session = DOMjudgeAPI.login(DOMJUDGE_ADMIN_USERNAME,
                                        DOMJUDGE_ADMIN_PASSWORD)

            # Admin login failed, just give a 'request failed' error flash
            if not session:
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            # Get the id of the 'viaduct_user' team category
            viaduct_user_cat_id = DOMjudgeAPI.get_viaduct_category_id(session)
            if not viaduct_user_cat_id:
                flash('Team category viaduct_user not found on DOMjudge.',
                      'danger')
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            # Check if the team already exists. This should normally
            # not be the case, but things can go wrong if we
            # create a new team anyway, since team names are not unique.
            user_team_id = DOMjudgeAPI.get_teamid_for_user(dom_teamname,
                                                           viaduct_user_cat_id,
                                                           session)
            if not user_team_id:
                r = DOMjudgeAPI.add_team(dom_teamname, dom_username,
                                         viaduct_user_cat_id, session)
                if not r:
                    return render_template('domjudge/problem/submit.htm',
                                           contest_id=contest_id)

                # Get the id of the newly created team
                user_team_id = DOMjudgeAPI.get_teamid_for_user(
                    dom_teamname, viaduct_user_cat_id, session)

            # Create the user
            r = DOMjudgeAPI.add_user(
                dom_username, dom_password,
                current_user.first_name + " " + current_user.last_name,
                current_user.email, user_team_id, session)

            if not r:
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

            DOMjudgeAPI.logout(session)

            # Login as the new user
            session = DOMjudgeAPI.login(dom_username, dom_password)

            if not session:
                return render_template('domjudge/problem/submit.htm',
                                       contest_id=contest_id)

        r = DOMjudgeAPI.submit(contest['shortname'], language,
                               problem['shortname'], file, session)
        if not r:
            return render_template('domjudge/problem/submit.htm',
                                   contest_id=contest_id)
        flash(_("Submission successful."))
        return redirect(url_for('domjudge.contest_view',
                                contest_id=contest_id))
    else:
        return render_template('domjudge/problem/submit.htm',
                               **locals())


@blueprint.route('/contest/<int:contest_id>/submissions/')
@login_required
def contest_submissions_view(contest_id):
    r = DOMjudgeAPI.request_get('api/contests')
    if not r:
        return render_template('domjudge/submissions.htm')

    if str(contest_id) not in r.json():
        flash(_("Contest does not exist."), 'danger')
        return redirect(url_for('domjudge.contest_list'))

    contest = r.json()[str(contest_id)]

    session = DOMjudgeAPI.login(DOMJUDGE_ADMIN_USERNAME,
                                DOMJUDGE_ADMIN_PASSWORD)

    # Admin login failed, just give a 'request failed' error flash
    if not session:
        return render_template('domjudge/submissions.htm')

    r = DOMjudgeAPI.request_get('api/submissions?cid={}'.format(contest_id),
                                session=session)
    if not r:
        return render_template('domjudge/submissions.htm')

    submissions = r.json()

    r = DOMjudgeAPI.request_get('api/judgings?cid={}'.format(contest_id),
                                session=session)
    if not r:
        return render_template('domjudge/submissions.htm')

    judgings = r.json()

    DOMjudgeAPI.logout(session)

    r = DOMjudgeAPI.request_get('api/languages')
    if not r:
        return render_template('domjudge/submissions.htm')

    languages = {}
    for lang in r.json():
        languages[lang['id']] = lang

    teams = get_teams()
    if not teams:
        return render_template('domjudge/submissions.htm')

    r = DOMjudgeAPI.request_get('api/problems?cid={}'.format(contest_id))
    if not r:
        return render_template('domjudge/submissions.htm')

    problems = {}
    for p in r.json():
        problems[p['id']] = p

    judgings_dict = {}
    for j in judgings:
        judgings_dict[j['submission']] = j

    submission_states = {'queued': _('Pending'),
                         'pending': _('Pending'),
                         'judging': _('Judging'),
                         'too-late': _('Too late'),
                         'correct': _('Correct'),
                         'compiler-error': _('Compiler Error'),
                         'timelimit': _('Timelimit'),
                         'run-error': _('Run Error'),
                         'no-output': _('No Output'),
                         'wrong-answer': _('Wrong Answer')
                         }

    for s in submissions:
        s['timestr'] = dt.datetime.fromtimestamp(s['time']).strftime(DT_FORMAT)
        m = VIA_USER_TEAM.match(teams[s['team']]['origname'])
        if m:
            s['userid'] = int(m.group(1))
        else:
            s['userid'] = -1

        s['team'] = teams[s['team']]['name']
        s['problem'] = problems[s['problem']]['name']
        s['language'] = languages[s['language']]['name']
        s_id = s['id']

        if s_id not in judgings_dict:
            outcome = 'pending'
        else:
            outcome = judgings_dict[s_id]['outcome']
            if outcome == 'queued':
                outcome = 'pending'

        s['result'] = submission_states[outcome]
        s['result_class'] = 'domjudge-submission-' + outcome

    submissions.sort(key=lambda x: x['time'], reverse=True)

    return render_template('domjudge/submissions.htm', user=current_user.id,
                           contest=contest, submissions=submissions)
