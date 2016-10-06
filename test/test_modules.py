import unittest
import re
import app


class TestPages(unittest.TestCase):

    class U:
        # Regular users should not have admin rights on any pages
        REGULAR_USERNAME = 'dummy@svia.nl'
        REGULAR_PASSWORD = 'dummy'
        # Admin users should have admin rights on all pages
        ADMIN_USERNAME = 'administrator@svia.nl'
        ADMIN_PASSWORD = 'wachtwoord'

    class C:
        HEADER = '\033[95m'
        AUTH = '\033[94m'
        OKGREEN = '\033[92m'
        NOTICE = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def create_app(self):
        return app

    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['CSRF_ENABLED'] = False
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()

        return

    def tearDown(self):
        return

    def login(self, username, password):
        return self.app.post('/sign-in/', data=dict(
            email=username,
            password=password
        ), headers={'Referer': 'home'}, follow_redirects=True)

    def logout(self):
        return self.app.get('/sign-out/', follow_redirects=True)

    def print_fail(self, string):
        print(TestPages.C.FAIL + string + TestPages.C.ENDC)

    def print_notice(self, string):
        print(TestPages.C.NOTICE + string + TestPages.C.ENDC)

    def print_ok(self, string):
        print(TestPages.C.OKGREEN + string + TestPages.C.ENDC)

    def print_auth(self, string):
        print(TestPages.C.AUTH + string + TestPages.C.ENDC)

    def print_header(self, string):
        print("\n" + TestPages.C.OKGREEN + TestPages.C.BOLD + string +
              TestPages.C.ENDC + TestPages.C.ENDC)

    def check_logged_in(self, username, rv):
        if "logged in" in str(rv.data) or 'ingelogd' in str(rv.data):
            self.print_ok("[Ok] - " + username + " is logged in")
            return True
        else:
            self.print_fail("[Warning] - " + username + " login failed. Abort")
            return False

    def check_pages(self, message):
        report = []

        for url in app.app.url_map._rules_by_endpoint:
            try:
                path = str(app.app.url_map._rules_by_endpoint[url][0])
                if ("delete" not in path and "remove" not in path and
                        "sign-out" not in path):

                    # substitude the path variables.
                    path = re.sub("\<(.+?)\>", "1", path)

                    rv = self.app.get(path, follow_redirects=False)

                    # Check for redirects.
                    if(rv._status_code == 302):
                        extra_info = " [redirect]"
                    else:
                        extra_info = ""

                    rv = self.app.get(path, follow_redirects=True)
                    rv_info = str(rv._status_code) + " on " + path + extra_info

                    # Test the status code, that has been returned.
                    if(rv._status_code == 200):
                        self.print_ok(message + " - [Ok] " + rv_info)
                    elif(rv._status_code == 403):
                        self.print_auth(message + " - [Notice] " + rv_info)
                    elif(rv._status_code == 404):
                        self.print_notice(message + " - [Notice] " + rv_info)
                    else:
                        self.print_fail(message + " - [Warning] " + rv_info)

            except Exception:
                self.print_fail(message + " - [Warning] Error in " + path)
                report.append(message + " - [Warning] Error in " + path)

        return report

    def test_modules(self):
        reports = []

        self.print_header("[Message] Testing all modules as Anonymous")

        reports.append(
            self.check_pages("User = Anonymous"))

        # Login as user.
        self.print_header("[Message] Testing all modules as user")
        rv = self.login(TestPages.U.REGULAR_USERNAME,
                        TestPages.U.REGULAR_PASSWORD)

        if not self.check_logged_in(TestPages.U.REGULAR_USERNAME, rv):
            return -1

        # Check modules as user.
        reports.append(
            self.check_pages("User = " + TestPages.U.REGULAR_USERNAME))
        self.logout()

        # Login as administrator
        self.print_header("[Message] Testing all modules as administrator")
        rv = self.login(TestPages.U.ADMIN_USERNAME, TestPages.U.ADMIN_PASSWORD)

        if not self.check_logged_in(TestPages.U.ADMIN_USERNAME, rv):
            return -1

        # Check modules as administrator
        reports.append(
            self.check_pages("User = " + TestPages.U.ADMIN_USERNAME))
        self.logout()

        # Print a short summary of all the encountered errors
        self.print_header("[Message] Errors summary")
        for report in reports:
            for page in report:
                self.print_fail("[Warning] on " + page)

if __name__ == '__main__':
    unittest.main()
