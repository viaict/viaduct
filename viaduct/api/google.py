import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from viaduct import application
import traceback
from flask import flash

# google calendar Settings > via_events > id
calendar_id = application.config['GOOGLE_CALENDAR_ID']

# Google API service account email
service_email = application.config['GOOGLE_SERVICE_EMAIL']

# name of the private key file
private_key = application.config['GOOGLE_API_KEY']


def build_service(service_type, api_version, scope):
    try:
        f = open(private_key, "rb")
        key = f.read()
        f.close()

        credentials = SignedJwtAssertionCredentials(
            service_email,
            key,
            scope=scope,
            sub='bestuur@via.uvastudent.org'  # "Log in" as the admin account
        )

        # Create an authorized http instance
        http = httplib2.Http()
        http = credentials.authorize(http)

        return build(service_type, api_version, http=http)
    except Exception:
        traceback.print_exc()
        return None


def build_calendar_service():
    return build_service('calendar', 'v3',
                         'https://www.googleapis.com/auth/calendar')


def build_groups_service():
    return build_service('admin', 'directory_v1',
                         ('https://www.googleapis.com'
                          '/auth/admin.directory.group'))


# Provide a calendar_id
def insert_activity(title="", description='', location="VIA kamer", start="",
                    end=""):
    service = build_calendar_service()

    if service:
        # Event to insert
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start, 'timeZone': 'Europe/Amsterdam'},
            'end': {'dateTime': end,     'timeZone': 'Europe/Amsterdam'}
        }

        try:
            return service.events() \
                .insert(calendarId=calendar_id, body=event) \
                .execute()
        except Exception:
            traceback.print_exc()
            flash('Er ging iets mis met het toevogen van het event aan de'
                  'Google Calender')
            return None


def update_activity(event_id, title="", description='', location="VIA Kamer",
                    start="", end=""):
    service = build_calendar_service()

    if service:
        # Event to update
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start, 'timeZone': 'Europe/Amsterdam'},
            'end': {'dateTime': end,     'timeZone': 'Europe/Amsterdam'}
        }

        try:
            return service.events() \
                .update(calendarId=calendar_id, eventId=event_id, body=event) \
                .execute()
        except Exception:
            traceback.print_exc()
            return insert_activity(title, description, location, start, end)


# Delete an event
def delete_activity(event_id):
    service = build_calendar_service()

    if service:
        try:
            return service.events() \
                .delete(calendarId=calendar_id, eventId=event_id) \
                .execute()
        except Exception:
            traceback.print_exc()
            flash('Er ging iets mis met het verwijderen van het event uit de'
                  'Google Calender, het kan zijn dat ie al verwijderd was')


def get_groups():
    service = build_groups_service()


def get_group_users():
    service = build_groups_service()
