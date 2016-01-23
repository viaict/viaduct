from viaduct import application
import requests, json

token = application.config['COPERNICA_API_KEY']
database_id = application.config['COPERNICA_DATABASE_ID']
actiepunt = application.config['COPERNICA_ACTIEPUNTEN']
activiteit = application.config['COPERNICA_ACTIVITEITEN']

def subscribeNewsletter(userID):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/fields?access_token=" + token
    data = {
        'Ingeschreven':'Ja'
    }
    requests.post(url, data)

def unsubscribeNewsletter(userID):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/fields?access_token=" + token
    data = {
        "Ingeschreven" : "Nee"
    }
    requests.post(url, data)

def addActivity(websiteID, name, eventID, amount=0, payed=False):
    id = viaIDtoCopernicaID(websiteID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + activiteit + "?access_token=" + token
    data = {
        "Naam" : name, 
        "Betaald" : "Ja" if (payed or amount == 0) else "Nee",
        "Bedrag": amount,
        "WebsiteID" : eventID
    }
    requests.post(url, data)

def payedActivity(userID, eventID, payed):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + activiteit + "?fields[]=WebsiteID%3D%3D"  + str(eventID) + "&access_token=" + token
    
    data = {
        "betaald" : "Ja" if payed else "Nee"
    }

    r = requests.get(url)
    for event in r.json()['data']:
        url = "https://api.copernica.com/subprofile/" + event['ID'] + "/fields?access_token=" + token
        requests.post(url, data)

def addActiepunt(websiteID, aID, groep, punt, status):
    id = viaIDtoCopernicaID(websiteID)
    if (id == -1): 
        return
    data = {
        "Groep": groep,
        "aID": aID,
        "Actiepunt": punt,
        "Status": status
    }
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + actiepunt + "?access_token=" + token
    requests.post(url, data)

def updateActiepunt(websiteID, aID, punt, status):
    id = viaIDtoCopernicaID(websiteID)
    if(id == -1):
        return
    data = {
        "Status" : status,
        "Actiepunt" : punt,
    }
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + actiepunt + "?fields[]=aID%3D%3D" + str(aID) + "&access_token=" + token
    r = requests.get(url)
    for punt in r.json()['data']:
        url = "https://api.copernica.com/subprofile/" + punt['ID'] + "/fields?access_token=" + token
        requests.post(url, data)

def viaIDtoCopernicaID(id):
    uID = -1
    url = "https://api.copernica.com/database/" + database_id + "/profiles?fields[]=WebsiteID%3D%3D" + str(id) + "&access_token=" + token

    r = requests.get(url)
    if len(r.json()['data']) > 0:
        uID = r.json()['data'][0]['ID']
    return uID


def newUser(mail, first, last, study, websiteID, studentnr, *args, **kwargs):
    if (viaIDtoCopernicaID(websiteID) != -1):
        return updateUser(websiteID, mail, first, last, study, args, kwargs)
    url = "https://api.copernica.com/database/" + database_id + "/profiles?access_token=" + token
    data = {
        "Emailadres" : mail,
        "Voornaam": first,
        "Achternaam": last,
        "Studie" : study,
        "WebsiteID": websiteID,
        "Studienummer" : studentnr,
        "Ingeschreven": kwargs['Ingeschreven'] if 'Ingeschreven' in kwargs else "Nee",
        "Lid": kwargs['Lid'] if 'Lid' in kwargs else "Nee",
        "VVV": kwargs['VVV'] if 'VVV' in kwargs else "Nee",
        "Bedrijfsinformatie": kwargs['Bedrijfsinformatie'] if 'Bedrijfsinformatie' in kwargs else "Nee",
        "Geboortedatum": kwargs['Geboortedatum'] if 'Geboortedatum' in kwargs else "0000-00-00",
    }
    print("Data to send to Copernica:")
    print(data)
    requests.post(url, data)

def updateUser(websiteID, mail, first, last, study, studentnr, *args, **kwargs):
    id = viaIDtoCopernicaID(websiteID)
    if(id == -1):
        print ("User bestaat nog niet")
        return newUser(mail, first, last, study, websiteID, args, kwargs)
    url = "https://api.copernica.com/database/" + database_id + "/profiles?fields[]=ID%3D%3D" + str(id) + "&access_token=" + token
    data = {
        "Emailadres" : mail,
        "Voornaam": first,
        "Achternaam": last,
        "Studie" : study,
        "Studienummer" : studentnr,
        "Ingeschreven": kwargs['Ingeschreven'] if 'Ingeschreven' in kwargs else "Ja",
        "Lid": kwargs['Lid'] if 'Lid' in kwargs else "Nee",
        "VVV": kwargs['VVV'] if 'VVV' in kwargs else "Nee",
        "Bedrijfsinformatie": kwargs['Bedrijfsinformatie'] if 'Bedrijfsinformatie' in kwargs else "Nee",
        "Geboortedatum": kwargs['Geboortedatum'] if 'Geboortedatum' in kwargs else "0000-00-00",
    }

    print("Data to send to Copernica:")
    print(data)

    requests.put(url, data)