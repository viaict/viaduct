from functools import wraps
from app import app, db
from app.models.user import User

import requests
import re
import logging

COPERNICA_ENABLED = app.config['COPERNICA_ENABLED']
API_TOKEN = app.config['COPERNICA_API_KEY']
DATABASE_ID = app.config['COPERNICA_DATABASE_ID']
SUBPROFILE_TASK = app.config['COPERNICA_ACTIEPUNTEN']
SUBPROFILE_ACTIVITY = app.config['COPERNICA_ACTIVITEITEN']

_logger = logging.getLogger(__name__)
_logger.info('COPERNICA_ENABLED={}'.format(COPERNICA_ENABLED))


def copernica_enabled(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not COPERNICA_ENABLED:
            return False
        else:
            f(*args, **kwargs)
    return wrapped


@copernica_enabled
def update_newsletter(user, subscribe=True):
    """Update the newsletter preferences of the user."""
    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/fields?access_token=" + API_TOKEN)
    data = {'Ingeschreven': 'Ja' if subscribe else "Nee"}
    requests.post(url, data)


@copernica_enabled
def add_subprofile(subprofile, user_id, data):
    """Create a news subprofile for for a user."""
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + str(user_id))

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?access_token=" + API_TOKEN)
    requests.post(url, data)


@copernica_enabled
def update_subprofile(subprofile, user_id, entry_id, data):
    """
    Update subprofile of a user in the copernica database.

    This is done by first quering all the subprofiles of a profile with
    matchting viaductID. When profiles are found, all of them are updated with
    the new data.
    """
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + str(user_id))

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?fields[]=viaductID%3D%3D" +
           str(entry_id) + "&access_token=" + API_TOKEN)

    r = requests.get(url)
    rv = [r]
    for entry in r.json()['data']:
        url = ("https://api.copernica.com/subprofile/" + entry['ID'] +
               "/fields?access_token=" + API_TOKEN)
        rv.append(requests.post(url, data))

    return rv


@copernica_enabled
def update_user(user, subscribe=False):
    data = {
        "Emailadres": user.email,
        "Voornaam": user.first_name,
        "Achternaam": user.last_name,
        "Studie": user.education.name if user.education else "Other",
        "Studienummer": user.student_id,
        "Lid": "Ja" if user.has_paid else "Nee",
        "Alumnus": "Ja" if user.alumnus else "Nee",
        "VVV": "Ja" if user.favourer else "Nee",
        "Bedrijfsinformatie": "Ja" if user.receive_information else "Nee",
        "Geboortedatum": (user.birth_date.strftime(app.config['DATE_FORMAT'])
                          if user.birth_date else "0000-00-00"),
        "WebsiteID": user.id
    }
    if subscribe:
        data["Ingeschreven"] = "Ja"

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
               "/profiles?fields[]=ID%3D%3D" + str(user.copernica_id) +
               "&access_token=" + API_TOKEN)
        requests.put(url, data)
    return True
