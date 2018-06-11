from app import app

from flask import flash
from flask_babel import _

import requests
from requests.exceptions import RequestException
import datetime as dt


class DOMjudgeAPI:
    @staticmethod
    def flash_error():
        flash(_("Request to DOMjudge server failed"), 'danger')

    @staticmethod
    def request_get(url, session=None):
        DOMJUDGE_URL = app.config['DOMJUDGE_URL']

        if not session:
            session = requests
        try:
            r = session.get(DOMJUDGE_URL + url, timeout=(5, 5))
        except RequestException:
            DOMjudgeAPI.flash_error()
            return None

        if r.status_code != 200:
            DOMjudgeAPI.flash_error()
            return None

        return r

    @staticmethod
    def request_post(url, data, files={},
                     session=None, flash_on_error=True):
        DOMJUDGE_URL = app.config['DOMJUDGE_URL']

        if not session:
            session = requests.Session()
        try:
            r = session.post(DOMJUDGE_URL + url, data=data,
                             files=files, timeout=(5, 5))
        except RequestException as e:
            if flash_on_error:
                DOMjudgeAPI.flash_error()
            return (False, e, session)

        if r.status_code >= 400:
            if flash_on_error:
                DOMjudgeAPI.flash_error()
            return (False, r, session)

        return (True, r, session)

    @staticmethod
    def login(username, password, flash_on_error=True):
        form_data = {
            'cmd': 'login',
            'login': username,
            'passwd': password
        }

        (result, _, session) = DOMjudgeAPI.request_post(
            'public/login.php', form_data, flash_on_error=flash_on_error)

        if result:
            return session
        return None

    @staticmethod
    def logout(session):
        DOMjudgeAPI.request_get('auth/logout.php', session=session)

    @staticmethod
    def add_user(username, password, full_name, email, teamid, session):
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

        (result, r, _) = DOMjudgeAPI.request_post(
            'jury/edit.php', form_data, session=session)

        if result:
            return r
        return None

    @staticmethod
    def add_team(name, member, categoryid, session):
        DT_FORMAT = app.config['DT_FORMAT']

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

        (result, r, _) = DOMjudgeAPI.request_post(
            'jury/edit.php', form_data, session=session)

        if result:
            return r
        return None

    @staticmethod
    def get_viaduct_category_id(session):
        r = DOMjudgeAPI.request_get("api/categories", session=session)
        if not r:
            return None

        for category in r.json():
            if category['name'] == 'viaduct_user':
                return category['categoryid']

        return None

    @staticmethod
    def get_teamid_for_user(name, viaduct_user_cat_id, session):
        r = DOMjudgeAPI.request_get('api/teams?category={}'.format(
            viaduct_user_cat_id), session=session)
        if not r:
            return None
        for team in r.json():
            if team['name'] == name:
                return team['id']

        return None

    @staticmethod
    def get_teamid_for_userid(id, viaduct_user_cat_id, session):
        r = DOMjudgeAPI.request_get('api/teams?category={}'.format(
            viaduct_user_cat_id), session=session)
        if not r:
            return None
        for team in r.json():
            if team['name'] == "via_user_team_" + str(id):
                return team['id']

        return None

    @staticmethod
    def get_teamname_for_teamid(teamid, viaduct_user_cat_id, session):
        r = DOMjudgeAPI.request_get('api/teams?category={}'.format(
            viaduct_user_cat_id), session=session)
        if not r:
            return None
        for team in r.json():
            if team['id'] == teamid:
                return team['name']

        return None

    @staticmethod
    def submit(contest_shortname, language_id, problem_shortname,
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
        (result, r, _) = DOMjudgeAPI.request_post('api/submissions', form_data,
                                                  files=files, session=session)
        if result:
            return r
