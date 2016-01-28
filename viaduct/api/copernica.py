import sys
import requests
import threading
import traceback

from flask import flash
from flask.ext.babel import _
from functools import wraps
from viaduct import application
from viaduct.api import google
from viaduct.models.user import User

API_TOKEN = application.config['COPERNICA_API_KEY']
DATABASE_ID = application.config['COPERNICA_DATABASE_ID']
SUBPROFILE_TASK = application.config['COPERNICA_ACTIEPUNTEN']
SUBPROFILE_ACTIVITY = application.config['COPERNICA_ACTIVITEITEN']


def copernica_failsafe(f):
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
# def subscribeNewsletter(userID):
# def unsubscribeNewsletter(userID):
def update_newsletter(userID, subscribe=True):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = ("https://api.copernica.com/profile/" + str(id) +
           "/fields?access_token=" + API_TOKEN)
    data = {
        'Ingeschreven': 'Ja' if subscribe else "Nee"
    }
    requests.post(url, data)


@copernica_failsafe
# def addActivity(websiteID, name, eventID, amount=0, payed=False,
def add_subprofile(subprofile, user_id, data):
    user = User.query.filter(id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + user_id)

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?access_token=" + API_TOKEN)
    requests.post(url, data)


@copernica_failsafe
# def reserveActivity(userID, eventID, reserve):
def update_subprofile(subprofile, user_id, entry_id, data):
    user = User.query.filter(id == user_id).first()
    if not user:
        raise KeyError('Cannot find user with id: ' + user_id)

    url = ("https://api.copernica.com/profile/" + str(user.copernica_id) +
           "/subprofiles/" + subprofile + "?fields[]=viaductID%3D%3D" +
           entry_id + "&access_token=" + API_TOKEN)

    r = requests.get(url)
    for entry in r.json()['data']:
        url = ("https://api.copernica.com/subprofile/" + entry['ID'] +
               "/fields?access_token=" + API_TOKEN)
        requests.post(url, data)


# def payedActivity(userID, eventID, payed):
# def addActiepunt(websiteID, aID, groep, punt, status):
# def updateActiepunt(websiteID, aID, punt, status):

@copernica_failsafe
def viaIDtoCopernicaID(id):
    raise TypeError('SHIT IS FOUT')
    uID = -1
    url = ("https://api.copernica.com/database/" + DATABASE_ID +
           "/profiles?fields[]=WebsiteID%3D%3D" + str(id) +
           "&access_token=" + API_TOKEN)

    r = requests.get(url)
    if len(r.json()['data']) > 0:
        uID = r.json()['data'][0]['ID']
    return uID


@copernica_failsafe
def newUser(mail, first, last, study, websiteID, studentnr, *args, **kwargs):
    threading.Thread(target=newUser_thread,
                     args=(mail, first, last, study, websiteID, studentnr),
                     kwargs=kwargs).start()


def newUser_thread(mail, first, last, study, websiteID, studentnr, *args,
                   **kwargs):
    if (viaIDtoCopernicaID(websiteID) != -1):
        return updateUser(websiteID, mail, first, last, study, args, kwargs)
    url = ("https://api.copernica.com/database/" + DATABASE_ID +
           "/profiles?access_token=" + API_TOKEN)
    data = {
        "Emailadres": mail,
        "Voornaam": first,
        "Achternaam": last,
        "Studie": study,
        "WebsiteID": websiteID,
        "Studienummer": studentnr,
        "Ingeschreven": (kwargs['Ingeschreven']
                         if 'Ingeschreven' in kwargs else "Nee"),
        "Lid": kwargs['Lid'] if 'Lid' in kwargs else "Nee",
        "VVV": kwargs['VVV'] if 'VVV' in kwargs else "Nee",
        "Bedrijfsinformatie": (kwargs['Bedrijfsinformatie']
                               if 'Bedrijfsinformatie' in kwargs else "Nee"),
        "Geboortedatum": (kwargs['Geboortedatum']
                          if 'Geboortedatum' in kwargs else "0000-00-00"),
    }
    requests.post(url, data)


@copernica_failsafe
def updateUser(websiteID, mail, first, last, study, studentnr,
               *args, **kwargs):
    id = viaIDtoCopernicaID(websiteID)
    if(id == -1):
        print ("User bestaat nog niet")
        return newUser(mail, first, last, study, websiteID, args, kwargs)
    url = ("https://api.copernica.com/database/" + DATABASE_ID +
           "/profiles?fields[]=ID%3D%3D" + str(id) + "&access_token=" +
           API_TOKEN)
    data = {
        "Emailadres": mail,
        "Voornaam": first,
        "Achternaam": last,
        "Studie": study,
        "Studienummer": studentnr,
        "Ingeschreven": (kwargs['Ingeschreven']
                         if 'Ingeschreven' in kwargs else "Ja"),
        "Lid": kwargs['Lid'] if 'Lid' in kwargs else "Nee",
        "VVV": kwargs['VVV'] if 'VVV' in kwargs else "Nee",
        "Bedrijfsinformatie": (kwargs['Bedrijfsinformatie']
                               if 'Bedrijfsinformatie' in kwargs else "Nee"),
        "Geboortedatum": (kwargs['Geboortedatum']
                          if 'Geboortedatum' in kwargs else "0000-00-00"),
    }
    requests.put(url, data)
