import os, httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from viaduct import application

# google calendar Settings > via_events > id
via_calendar_id = "bka8j77cis5ffr2pokn5ef5cso@group.calendar.google.com"
via_lezingen_id = "dp1qibentsgl50vj6lt31ekk3g@group.calendar.google.com"

# Google API service account email
service_email = "913209651562-jorctggrfuanpqrc5hvmu0ep3rmg2tca@developer.gserviceaccount.com"

# name of the private key file
private_key = application.config['GOOGLE_API_KEY']


def build_service():
    f = file(os.path.dirname(os.path.abspath(__file__)) + "/" + private_key, "rb")
    key = f.read()
    f.close()

    credentials = SignedJwtAssertionCredentials(
    service_email,
    key,
    scope="https://www.googleapis.com/auth/calendar"
    )

  # Create an authorized http instance
    http = httplib2.Http()
    http = credentials.authorize(http)

    return build("calendar", "v3", http=http)


# Helper method to insert a via activity
def insert_activity(title, location, start, end):
    return insert_event(
      title,
      location,
      start,
      end,
      via_calendar_id
    )


# Helper method to insert a via_lezing
def insert_lecture(title, location, start, end):
    return insert_event(
      title,
      location,
      start,
      end,
      via_lezingen_id
    )


# Provide a calendar_id
def insert_event(title="", location="VIA kamer", start="", end="", calendar_id=None):
    service = build_service()

    # Event to insert
    event = {
      'summary': title,
      'location': location,
      'start': {'dateTime': start, 'timeZone':'Europe/Amsterdam'},
      'end': {'dateTime': end,     'timeZone':'Europe/Amsterdam'}
    }

    return service.events() \
            .insert(calendarId=calendar_id, body=event) \
            .execute()


def update_activity(event_id, title, location, start, end):
    return update_event(
      event_id,
      title,
      location,
      start,
      end,
      via_calendar_id
    )


def update_lecture(event_id, title, location, start, end):
    return update_event(
      event_id,
      title,
      location,
      start,
      end,
      via_lezingen_id
    )


def update_event(event_id, title="", location="VIA Kamer", start="", end="", calendar_id=None):
    service = build_service()

    # Event to update
    event = {
      'summary': title,
      'location': location,
      'start': {'dateTime': start, 'timeZone':'Europe/Amsterdam'},
      'end': {'dateTime': end,     'timeZone':'Europe/Amsterdam'}
    }

    return service.events() \
            .update(calendarId=calendar_id, eventId=event_id, body=event) \
            .execute()


def delete_activity(event_id):
    return delete_event(event_id, via_calendar_id)


def delete_lecture(event_id):
    return delete_event(event_id, via_lezingen_id)


# Delete an event
def delete_event(event_id, calendar_id=None):
    service = build_service()

    return service.events() \
            .delete(calendarId=calendar_id, eventId=event_id) \
            .execute()

