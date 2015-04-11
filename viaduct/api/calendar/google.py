import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from viaduct import application
import traceback

# google calendar Settings > via_events > id
via_calendar_id = "bka8j77cis5ffr2pokn5ef5cso@group.calendar.google.com"

# Google API service account email
service_email = ('614222921385-1lrc4bkrq51mb4ra4dl8g2f1hi8232e2'
                 '@developer.gserviceaccount.com')

# name of the private key file
private_key = application.config['GOOGLE_API_KEY']


def build_service():
    try:
        f = open(private_key, "rb")
        key = f.read()
        f.close()

        credentials = SignedJwtAssertionCredentials(
            service_email,
            key,
            scope="https://www.googleapis.com/auth/calendar",
            sub='bestuur@via.uvastudent.org'
        )

        # Create an authorized http instance
        http = httplib2.Http()
        http = credentials.authorize(http)

        return build("calendar", "v3", http=http)
    except Exception:
        traceback.print_exc()
        return None


def insert_activity(title, description, location, start, end):
    """Helper method to insert a via activity"""
    return insert_event(
        title,
        description,
        location,
        start,
        end,
        via_calendar_id
    )


# Provide a calendar_id
def insert_event(title="", description='', location="VIA kamer", start="",
                 end="", calendar_id=None):
    service = build_service()

    if service:
        # Event to insert
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start, 'timeZone': 'Europe/Amsterdam'},
            'end': {'dateTime': end,     'timeZone': 'Europe/Amsterdam'}
        }

        if application.debug:
            return None
        return service.events() \
            .insert(calendarId=calendar_id, body=event) \
            .execute()


def update_activity(event_id, title, description, location, start, end):
    return update_event(
        event_id,
        title,
        description,
        location,
        start,
        end,
        via_calendar_id
    )


def update_event(event_id, title="", description='', location="VIA Kamer",
                 start="", end="", calendar_id=None):
    service = build_service()

    if service:
        # Event to update
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start, 'timeZone': 'Europe/Amsterdam'},
            'end': {'dateTime': end,     'timeZone': 'Europe/Amsterdam'}
        }

        if application.debug:
            return None

        return service.events() \
            .update(calendarId=calendar_id, eventId=event_id, body=event) \
            .execute()


def delete_activity(event_id):
    return delete_event(event_id, via_calendar_id)


# Delete an event
def delete_event(event_id, calendar_id=None):
    service = build_service()

    if service:
        return service.events() \
            .delete(calendarId=calendar_id, eventId=event_id) \
            .execute()
