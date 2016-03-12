import unittest
import os
import re
from glob import glob
from flask import json

import app

class user:
    # Regular user should not have admin rights on any pages
    REGULAR_USERNAME = 'dummy@svia.nl'
    REGULAR_PASSWORD = 'dummy'
    # Admin user should have admin rights on all pages
    ADMIN_USERNAME = 'administrator@svia.nl'
    ADMIN_PASSWORD = 'wachtwoord'

class bcolors:
    HEADER = '\033[95m'
    AUTH = '\033[94m'
    OKGREEN = '\033[92m'
    NOTICE = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class testPages(unittest.TestCase):
    def create_app(self):
        return application

    def setUp(self):
        app.application.config['TESTING'] = True
        app.application.config['CSRF_ENABLED'] = False
        app.application.config['WTF_CSRF_ENABLED'] = False
        self.application = app.application.test_client()

        return

    def tearDown(self):
        return

    def login(self, username, password):
        return self.application.post('/sign-in/', data=dict(
            email=username,
            password=password
        ), headers={'Referer': 'home'}, follow_redirects=True)

    def logout(self):
        return self.application.get('/sign-out/', follow_redirects=True)

    def printFail(self, string):
        print(bcolors.FAIL + string + bcolors.ENDC)

    def printNotice(self, string):
        print(bcolors.NOTICE + string + bcolors.ENDC)

    def printOk(self, string):
        print(bcolors.OKGREEN + string + bcolors.ENDC)

    def printOk(self, string):
        print(bcolors.OKGREEN + string + bcolors.ENDC)

    def printAuth(self, string):
        print(bcolors.AUTH + string + bcolors.ENDC)

    def printHeader(self, string):
        print("\n" + bcolors.OKGREEN + bcolors.BOLD + string + bcolors.ENDC + bcolors.ENDC)


    def checkLoggedIn(self, username, rv):
        if "You&#39;ve been signed in successfully." in rv.data:
            self.printOk("[Ok] - " + username + " is logged in")
            return True
        else:
            self.printFail("[Warning] - " + username + " login failed. Abort")
            return False      

    def checkPages(self, message):
        report = []

        for url in app.application.url_map._rules_by_endpoint:
            try:
                path = str(app.application.url_map._rules_by_endpoint[url][0])
                if not "delete" in path and not "remove" in path and not "sign-out" in path:

                    """ substitude the path variables """
                    path = re.sub("\<(.+?)\>", "1", path)

                    rv = self.application.get(path, follow_redirects=False)

                    """ Check for redirects """
                    if(rv._status_code == 302):
                        extra_info = " [redirect]"
                    else:
                        extra_info = ""

                    rv = self.application.get(path, follow_redirects=True)

                    rv_info = str(rv._status_code) + " on " +  path + extra_info

                    """ Test the status code, that has been returned """
                    if(rv._status_code == 200):
                        self.printOk(message + " - [Ok] " + rv_info)
                    elif(rv._status_code == 403):
                        self.printAuth(message + " - [Notice] " + rv_info)
                    elif(rv._status_code == 404):
                        self.printNotice(message + " - [Notice] " + rv_info)
                    else:
                        self.printFail(message + " - [Warning] " + rv_info)

            except Exception as exception:
                self.printFail(message + " - [Warning] Error in " + path)
                report.append(message + " - [Warning] Error in " + path)
                pass

        return report

    def test_Modules(self):
        reports = []

        self.printHeader("[Message] Testing all modules as Anonymous")

        reports.append(self.checkPages("User = Anonymous"))
        
        """ Login as user """
        self.printHeader("[Message] Testing all modules as user")
        rv = self.login(user.REGULAR_USERNAME, user.REGULAR_PASSWORD)

        if not self.checkLoggedIn(user.REGULAR_USERNAME, rv):
            return -1;

        """ Check modules as user """
        reports.append(self.checkPages("User = " + user.REGULAR_USERNAME))
        self.logout()
        
        """ Login as administrator """
        self.printHeader("[Message] Testing all modules as administrator")
        rv = self.login(user.ADMIN_USERNAME, user.ADMIN_PASSWORD)

        if not self.checkLoggedIn(user.ADMIN_USERNAME, rv):
            return -1;

        """ Check modules as administrator """
        reports.append(self.checkPages("User = " + user.ADMIN_USERNAME))
        self.logout()

        """ Print a short summary of all the encountered errors """
        self.printHeader("[Message] Errors summary")
        for report in reports:
            for page in report:
                self.printFail("[Warning] on " + page)
       

if __name__ == '__main__':
    unittest.main()
