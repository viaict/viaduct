from viaduct import app
import requests, json, threading

token = app.config['COPERNICA_API_KEY']
database_id = app.config['COPERNICA_DATABASE_ID']
actiepunt = app.config['COPERNICA_ACTIEPUNTEN']
activiteit = app.config['COPERNICA_ACTIVITEITEN']

def subscribeNewsletter(userID):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/fields?access_token=" + token
    data = {
        'Ingeschreven':'Ja'
    }
    requests.post(url, data)
    # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])

def unsubscribeNewsletter(userID):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/fields?access_token=" + token
    data = {
        "Ingeschreven" : "Nee"
    }
    requests.post(url, data)
    # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])

def addActivity(websiteID, name, eventID, amount=0, payed=False, reserve=False):
    threading.Thread(target=addActivity_thread, args=(websiteID, name, eventID, amount, payed)).start()

def addActivity_thread(websiteID, name, eventID, amount=0, payed=False, reserve=False):
    id = viaIDtoCopernicaID(websiteID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + activiteit + "?access_token=" + token
    data = {
        "Naam" : name, 
        "Betaald" : "Ja" if (payed or amount == 0) else "Nee",
        "Reserve" : "Ja" if reserve else "Nee",
        "Bedrag": amount,
        "WebsiteID" : eventID
    }
    requests.post(url, data)
    # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])

def reserveActivity(userID, eventID, reserve):
    threading.Thread(target=reserveActivity_thread, args=(userID, eventID, reserve)).start()

def reserveActivity_thread(userID, eventID, reserve):
    id = viaIDtoCopernicaID(userID)
    if(id == -1):
        return
    url = "https://api.copernica.com/profile/" + str(id) + "/subprofiles/" + activiteit + "?fields[]=WebsiteID%3D%3D"  + str(eventID) + "&access_token=" + token
    
    data = {
        "Reserve" : "Ja" if reserve else "Nee"
    }

    r = requests.get(url)
    for event in r.json()['data']:
        url = "https://api.copernica.com/subprofile/" + event['ID'] + "/fields?access_token=" + token
        requests.post(url, data)

def payedActivity(userID, eventID, payed):
    threading.Thread(target=payedActivity_thread, args=(userID, eventID, payed)).start()

def payedActivity_thread(userID, eventID, payed):
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
        # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])
        requests.post(url, data)

def addActiepunt(websiteID, aID, groep, punt, status):
    threading.Thread(target=addActiepunt_thread, args=(websiteID, aID, groep, punt, status)).start()

def addActiepunt_thread(websiteID, aID, groep, punt, status):
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
    threading.Thread(target=updateActiepunt_thread, args=(websiteID, aID, punt, status)).start()

def updateActiepunt_thread(websiteID, aID, punt, status):
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
        # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])

def viaIDtoCopernicaID(id):
    uID = -1
    url = "https://api.copernica.com/database/" + database_id + "/profiles?fields[]=WebsiteID%3D%3D" + str(id) + "&access_token=" + token

    r = requests.get(url)
    if len(r.json()['data']) > 0:
        uID = r.json()['data'][0]['ID']
    return uID

def newUser(mail, first, last, study, websiteID, studentnr, *args, **kwargs):
    threading.Thread(target=newUser_thread, args=(mail, first, last, study, websiteID, studentnr), kwargs=kwargs).start()

def newUser_thread(mail, first, last, study, websiteID, studentnr, *args, **kwargs):
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
    # print("Data to send to Copernica:")
    # print(data)
    requests.post(url, data)
    # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "post", url, json.dumps(data)])

def updateUser(websiteID, mail, first, last, study, studentnr, *args, **kwargs):
    threading.Thread(target=updateUser_thread, args=(websiteID, mail, first, last, study, studentnr), kwargs=kwargs).start()

def updateUser_thread(websiteID, mail, first, last, study, studentnr, *args, **kwargs):
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
    requests.put(url, data)
    # subprocess.Popen(["venv/bin/python", "scripts/copernica_sender.py", "put", url, json.dumps(data)])