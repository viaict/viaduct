LANGUAGES = {
    'en': 'English',
    'nl': 'Nederlands'
}

MIN_PASSWORD_LENGTH = 6

# Path to Google p12 key file, change for real use
GOOGLE_API_KEY = './GoogleAPI.pem'

# One date format string to rule them all (use this in strftime)
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"
DT_FORMAT = "{} {}".format(DATE_FORMAT, TIME_FORMAT)

# Activity datetime format used in activity.py
ACT_DT_FORMAT = "%a. %d %b %Y (%H:%M)"
