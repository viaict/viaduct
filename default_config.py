from datetime import date

import os
import logging


class Config:
    base_path = os.path.abspath(os.path.dirname(__file__))

    DEBUG = True

    DATABASE_CONNECT_OPTIONS = {}

    SECRET_KEY = 'secret'  # Change this for real use

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = ''  # Change this for real use

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = ''   # Change this for real use
    RECAPTCHA_PRIVATE_KEY = ''  # Change this for real use
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    EXAMINATION_UPLOAD_FOLDER = 'app/static/uploads/examinations'
    SUMMARY_UPLOAD_FOLDER = 'app/static/uploads/summaries'
    UPLOAD_DIR = 'app/static/files/'
    FILE_DIR = '/static/files/'

    HASHFS_ROOT_DIR = 'app/uploads/'

    # One date format string to rule them all (use this in strftime)
    DATE_FORMAT = "%d-%m-%Y"
    TIME_FORMAT = "%H:%M"
    DT_FORMAT = "{} {}".format(DATE_FORMAT, TIME_FORMAT)
    # Activity datetime format used in activity.py
    ACT_DT_FORMAT = "%a. %d %b %Y (%H:%M)"
    MIN_PASSWORD_LENGTH = 6

    LANGUAGES = {
        'en': 'English',
        'nl': 'Nederlands'
    }

    # Teacher's elections configuration
    ELECTIONS_NOMINATE_START = date(2014, 12, 12)
    ELECTIONS_VOTE_START = date(2015, 1, 5)
    ELECTIONS_VOTE_END = date(2015, 1, 16)

    GOOGLE_API_KEY = ''   # Path to Google p12 key file, change for real use
    GOOGLE_SERVICE_EMAIL = 'test@developer.gserviceaccount.com'  # change this
    GOOGLE_CALENDAR_ID = ''  #

    # ict@svia.nl
    GITLAB_TOKEN = "Insert GitLab API access"

    # Mollie config
    MOLLIE_URL = 'https://api.mollie.nl/v1/payments/'
    MOLLIE_TEST_KEY = 'test_SOMEAPIKEY'
    MOLLIE_KEY = ''
    MOLLIE_REDIRECT_URL = 'https://svia.nl/mollie/check/'
    MOLLIE_TEST_MODE = True

    COPERNICA_ENABLED = False
    COPERNICA_API_KEY = ""
    COPERNICA_DATABASE_ID = ""
    COPERNICA_ACTIEPUNTEN = ""
    COPERNICA_ACTIVITEITEN = ""
    COPERNICA_NEWSLETTER_TOKEN = "test123"

    DOMJUDGE_ADMIN_USERNAME = "viaduct"
    DOMJUDGE_ADMIN_PASSWORD = ""
    DOMJUDGE_URL = "http://localhost:80/"
    DOMJUDGE_USER_PASSWORD = ""

    # Additional user attributes to be send to sentry.io.
    SENTRY_USER_ATTRS = ['name', 'email']

    # Log levels: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    LOG_LEVEL = logging.DEBUG

    PRIVACY_POLICY_URL_NL = '/static/via_privacy_policy_nl.pdf'
    PRIVACY_POLICY_URL_EN = '/static/via_privacy_policy_en.pdf'
