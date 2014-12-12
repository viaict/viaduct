import os
from datetime import date

base_path = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'secret_key'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://viaduct:viaduct@localhost/viaduct'
DATABASE_CONNECT_OPTIONS = {}

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret_key'

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_OPTIONS = {'theme': 'white'}

EXAMINATION_UPLOAD_FOLDER = 'viaduct/static/uploads/examinations'
UPLOAD_DIR = 'viaduct/static/files/'
FILE_DIR = '/static/files/'

# One date format string to rule them all (use this in for example strftime)
DATE_FORMAT = "%Y-%m-%d"

ADMIN_PW = 'wachtwoord'

GOOGLE_API_KEY = ''

GMAIL_MAIL_ACCOUNT = {
    'username': 'wachtwoordvergeten.via@gmail.com',
    'password': 'vergeetJeWachtwoordDanOokNietsukkeltje'
    }

# ict@svia.nl
JIRA_ACCOUNT = {
    'username': 'ictvia',
    'password': 'createIssueAccountVIA'
    }

# Mollie config
MOLLIE_URL = ''
MOLLIE_TEST_KEY = ''
MOLLIE_KEY = ''
MOLLIE_REDIRECT_URL = ''
MOLLIE_TEST_MODE = True

LANGUAGES = {
    'en': 'English',
    'nl': 'Nederlands'
    }

# Teacher's elections configuration
ELECTIONS_NOMINATE_START = date(2014, 12, 12)
ELECTIONS_VOTE_START = date(2015, 1, 5)
ELECTIONS_VOTE_END = date(2015, 1, 9)
