import sys
import requests
import traceback
import re

from flask import flash
from flask.ext.babel import _
from functools import wraps
from app import app, db
from app.api import google
from app.models.user import User

API_TOKEN = app.config['COPERNICA_API_KEY']
DATABASE_ID = app.config['COPERNICA_DATABASE_ID']
SUBPROFILE_TASK = app.config['COPERNICA_ACTIEPUNTEN']
SUBPROFILE_ACTIVITY = app.config['COPERNICA_ACTIVITEITEN']


def copernica_failsafe(f):
    """
    A decorator that catches any unknown errors and sends out an e-mail to
    debug_copernica@svia.nl.
    """
    @wraps(f)
    def df(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            ex_tp, ex, tb = sys.exc_info()
            flash(_("Something went wrong while pushing information to " +
                    "copernica"))
            google.send_email('debug_copernica@svia.nl', "Copernica Error!",
                              "email/copernica_debugging.htm",
                              error=traceback.format_exception(ex_tp, ex, tb))
    return df


@copernica_failsafe
def update_newsletter(user, subscribe=True):
    """
    Update the newsletter preferences of the user
    """
    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/fields?access_token=" + API_TOKEN)
    data = {
        'Ingeschreven': 'Ja' if subscribe else "Nee"
    }
    requests.post(url, data)


@copernica_failsafe
def add_subprofile(subprofile, user_id, data):
    """
    Create a news subprofile for for a user.
    """
    user = User.query.filter(id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + user_id)

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?access_token=" + API_TOKEN)
    requests.post(url, data)


@copernica_failsafe
def update_subprofile(subprofile, user_id, entry_id, data):
    """
    Updates a subprofile of a user. This is done by first quering all the
    subprofiles of a profile with matchting viaductID. When profiles are found,
    all of them are updated with the new data.
    """
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + str(user_id))

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?fields[]=viaductID%3D%3D" +
           str(entry_id) + "&access_token=" + API_TOKEN)

    print(url)
    r = requests.get(url)
    rv = [r]
    for entry in r.json()['data']:
        url = ("https://api.copernica.com/subprofile/" + entry['ID'] +
               "/fields?access_token=" + API_TOKEN)
        rv.append(requests.post(url, data))

    return rv


@copernica_failsafe
def update_user(user):
    data = {
        "Emailadres": user.email,
        "Voornaam": user.first_name,
        "Achternaam": user.last_name,
        "Studie": user.education.name,
        "Studienummer": user.student_id,
        "Ingeschreven": "Ja" if user.has_payed else "Nee",
        "Lid": "Ja" if user.has_payed else "Nee",
        "VVV": "Ja" if user.favourer else "Nee",
        "Bedrijfsinformatie": "Ja" if user.receive_information else "Nee",
        "Geboortedatum": user.birth_date.strftime('%Y-%m-%d')
    }

    if not user.copernica_id or user.copernica_id == 0:
        url = ("https://api.copernica.com/database/" + DATABASE_ID +
               "/profiles?access_token=" + API_TOKEN)
        r = requests.post(url, data)

        # Regex to extract the copernica_id from the Location URL
        rx = re.compile('\/([0-9]+)\?')
        user.copernica_id = re.search(rx, r.headers['Location']).groups()[0]
        db.session.add(user)
        db.session.commit()
    else:
        url = ("https://api.copernica.com/database/" + DATABASE_ID +
               "/profiles?fields[]=ID%3D%3D" + str(id) + "&access_token=" +
               API_TOKEN)
        requests.put(url, data)
