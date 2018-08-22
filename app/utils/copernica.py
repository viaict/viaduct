import logging
import re
import requests
from functools import wraps

from app import app, db, constants
from app.models.user import User

_logger = logging.getLogger(__name__)


def copernica_enabled(f):

    @wraps(f)
    def wrapped(*args, **kwargs):
        enabled = app.config['COPERNICA_ENABLED']

        _logger.info(f'COPERNICA_ENABLED={enabled}')

        if not enabled:
            return False
        else:
            f(*args, **kwargs)
    return wrapped


@copernica_enabled
def update_newsletter(user, subscribe=True):
    """Update the newsletter preferences of the user."""
    url = "https://api.copernica.com/profile/{}/fields?access_token={}"
    url = url.format(user.copernica_id, app.config['COPERNICA_API_KEY'])
    data = {'Ingeschreven': 'Ja' if subscribe else "Nee"}
    requests.post(url, data)


@copernica_enabled
def add_subprofile(subprofile, user_id, data):
    """Create a news subprofile for for a user."""
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + str(user_id))

    url = "https://api.copernica.com/profile/{}/subprofiles/{}?access_token={}"
    url = url.format(user.copernica_id, subprofile,
                     app.config['COPERNICA_API_KEY'])
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

    url = "https://api.copernica.com/profile/{}/subprofiles/{}?fields[]=viaductID%3D%3D{}&access_token={}"  # noqa
    url = url.format(user.copernica_id, subprofile, entry_id,
                     app.config['COPERNICA_API_KEY'])

    r = requests.get(url)
    rv = [r]
    for entry in r.json()['data']:
        url = "https://api.copernica.com/subprofile/{}/fields?access_token={}"
        url = url.format(entry['ID'], app.config['COPERNICA_API_KEY'])
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
        "Geboortedatum": (user.birth_date.strftime(constants.DATE_FORMAT)
                          if user.birth_date else "0000-00-00"),
        "WebsiteID": user.id
    }
    if subscribe:
        data["Ingeschreven"] = "Ja"

    if not user.copernica_id or user.copernica_id == 0:
        url = "https://api.copernica.com/database/{}/profiles?access_token={}"
        url = url.format(app.config['COPERNICA_DATABASE_ID'],
                         app.config['COPERNICA_API_KEY'])
        r = requests.post(url, data)

        # Regex to extract the copernica_id from the Location URL
        rx = re.compile('/([0-9]+)\?')
        user.copernica_id = re.search(rx, r.headers['Location']).groups()[0]
        db.session.add(user)
        db.session.commit()
    else:
        url = "https://api.copernica.com/database/{}/profiles?fields[]=ID%3D%3D{}&access_token={}"  # noqa
        url = url.format(app.config['COPERNICA_DATABASE_ID'],
                         user.copernica_id, app.config['COPERNICA_API_KEY'])
        requests.put(url, data)
    return True
