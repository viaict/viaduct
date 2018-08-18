import dateutil.parser
import distutils.util
from flask import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

_logger = logging.getLogger(__name__)


class Config(object):

    def __init__(self, database_url):
        """
        Initialize the config

        Load the config values from the environment and do dynamic conversion.
        """

        # Database connection
        self.SECRET_KEY = str

        # Flask-WTForms recaptcha.
        self.RECAPTCHA_PUBLIC_KEY = str
        self.RECAPTCHA_PRIVATE_KEY = str

        # Google apps synchronization.
        self.GOOGLE_SERVICE_EMAIL = str
        self.GOOGLE_CALENDAR_ID = str

        # Election dates.
        self.ELECTIONS_NOMINATE_START = dateutil.parser.parse
        self.ELECTIONS_VOTE_START = dateutil.parser.parse
        self.ELECTIONS_VOTE_END = dateutil.parser.parse

        # Git lab token for bug report.
        self.GITLAB_TOKEN = str

        # Mollie payment provider config.
        self.MOLLIE_URL = str
        self.MOLLIE_KEY = str
        self.MOLLIE_REDIRECT_URL = str

        # Copernica e-mailing synchronization configuration.
        self.COPERNICA_ENABLED = distutils.util.strtobool
        self.COPERNICA_API_KEY = str
        self.COPERNICA_DATABASE_ID = str
        self.COPERNICA_ACTIEPUNTEN = str
        self.COPERNICA_ACTIVITEITEN = str
        self.COPERNICA_NEWSLETTER_TOKEN = str

        # DOMJudge competition integration
        self.DOMJUDGE_ADMIN_USERNAME = str
        self.DOMJUDGE_ADMIN_PASSWORD = str
        self.DOMJUDGE_URL = str
        self.DOMJUDGE_USER_PASSWORD = str

        # Sentry error capturing
        self.SENTRY_DSN = str
        self.ENVIRONMENT = str

        # URL for Athenaeum order page
        self.ATHENAEUM_URL = str

        # Privacy policy
        self.PRIVACY_POLICY_URL_EN = str
        self.PRIVACY_POLICY_URL_NL = str

        self.load_config(database_url=database_url)

        # These must be defined after `load_config`, since they are not
        # defined in the database.
        self.RECAPTCHA_OPTIONS = {'theme': 'white'}

        self.SENTRY_USER_ATTRS = ['name', 'email']
        self.SENTRY_CONFIG = {
            'environment': self.ENVIRONMENT
        }

        # Miscellaneous.
        self.DEBUG_TB_INTERCEPT_REDIRECTS = False
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

    def load_config(self, database_url):
        engine = create_engine(database_url)
        session = scoped_session(sessionmaker(bind=engine))

        settings = {s[0]: s[1] for s in
                    session.execute("SELECT key, value FROM setting")}

        for key in dir(self):
            if not key.isupper():
                continue

            func = getattr(self, key)
            if callable(func):
                value = func(settings[key])
                setattr(self, key, value)
                _logger.info(f"{key} = {value}")
            else:
                _logger.info(f"{key} type not defined as callable.")
