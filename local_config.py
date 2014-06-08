import os

base_path = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SECRET_KEY = 'secret_key'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_path,
                                                      'application.db')
DATABASE_CONNECT_OPTIONS = {}

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret_key'

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_OPTIONS = {'theme': 'white'}

EXAMINATION_UPLOAD_FOLDER = 'viaduct/static/uploads/examinations'
EXAMINATION_FILE_DIR = '/static/uploads/examinations'
UPLOAD_DIR = 'viaduct/static/files/'
FILE_DIR = '/static/files/'

# One date format string to rule them all (use this in for example strftime)
DATE_FORMAT = "%Y-%m-%d"

ADMIN_PW = 'wachtwoord'

GOOGLE_API_KEY = ''

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
