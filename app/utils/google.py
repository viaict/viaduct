import base64
import logging
from email.mime.text import MIMEText

import httplib2
from apiclient import errors
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from flask import flash, render_template

from app import app, sentry

# google calendar Settings > via_events > id
calendar_id = app.config['GOOGLE_CALENDAR_ID']

# Google API service account email
service_email = app.config['GOOGLE_SERVICE_EMAIL']

# name of the private key file
private_key = app.config['GOOGLE_API_KEY']

domain = 'svia.nl'

_logger = logging.getLogger(__name__)


def build_service(service_type, api_version, scope):
    try:
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            service_account_email=service_email,
            filename=private_key,
            scopes=[scope]).create_delegated("bestuur@svia.nl")

        # Create an authorized http instance
        http = httplib2.Http()
        http = credentials.authorize(http)

        return build(service_type, api_version, http=http)
    except Exception as e:
        _logger.error(e)
        sentry.captureException(e)
        return None


def build_calendar_service():
    return build_service('calendar', 'v3',
                         'https://www.googleapis.com/auth/calendar')


def build_groups_service():
    return build_service('admin', 'directory_v1',
                         ('https://www.googleapis.com'
                          '/auth/admin.directory.group'))


def build_gmail_service():
    return build_service('gmail', 'v1',
                         'https://www.googleapis.com/auth/gmail.send')


def get_group_api():
    return build_groups_service().groups()


def get_group_members_api():
    return build_groups_service().members()


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
            'end': {'dateTime': end, 'timeZone': 'Europe/Amsterdam'}
        }

        try:
            return service.events() \
                .insert(calendarId=calendar_id, body=event) \
                .execute()
        except Exception as e:
            _logger.error(e)
            sentry.captureException(e)
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
            'end': {'dateTime': end, 'timeZone': 'Europe/Amsterdam'}
        }

        try:
            return service.events() \
                .update(calendarId=calendar_id, eventId=event_id, body=event) \
                .execute()
        except Exception as e:
            _logger.error(e)
            sentry.captureException(e)
            return insert_activity(title, description, location, start, end)


# Delete an event
def delete_activity(event_id):
    service = build_calendar_service()

    if service:
        try:
            return service.events() \
                .delete(calendarId=calendar_id, eventId=event_id) \
                .execute()
        except Exception as e:
            sentry.captureException(e)
            _logger.error(e)
            flash('Er ging iets mis met het verwijderen van het event uit de'
                  'Google Calender, het kan zijn dat ie al verwijderd was')


def get_groups():
    api = get_group_api()
    return api.list(domain=domain).execute()['groups']


def get_group_by_name(listname):
    api = get_group_api()
    return api.get(groupKey=listname + '@' + domain).execute()


def get_group_id_by_name(listname):
    group = get_group_by_name(listname)
    if group is None:
        return None
    return group['id']


def get_group_members(listname):
    api = get_group_members_api()
    return api.list(groupKey=listname + '@' + domain).execute()


def create_group(groupname, listname):
    if app.debug:
        return
    api = get_group_api()
    email = listname + '@' + domain
    api.insert(body={'email': email, 'name': groupname}).execute()


def create_group_if_not_exists(groupname, listname):
    try:
        create_group(groupname, listname)
    except HttpError as e:
        if e.resp.status != 409:
            # Something else went wrong than the list already existing
            raise(e)


def add_email_to_group(email, listname):
    if app.debug:
        return
    api = get_group_members_api()
    list_id = listname + '@' + domain
    api.insert(groupKey=list_id,
               body={'email': email, 'role': 'MEMBER'}).execute()


def add_email_to_group_if_not_exists(email, listname):
    try:
        add_email_to_group(email, listname)
    except HttpError as e:
        if e.resp.status != 409:
            # Something else went wrong than the list already existing
            raise(e)


def remove_email_from_group_if_exists(email, listname):
    if app.debug:
        return
    api = get_group_members_api()
    try:
        api.delete(groupKey=listname + '@' + domain, memberKey=email).execute()
    except HttpError as e:
        if e.resp.status == 400:
            return
        if e.resp.status == 404:
            return
        raise(e)


def send_email(to, subject, email_template,
               sender='no-reply@svia.nl', **kwargs):
    """ Send an e-mail from the via-gmail

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    content: The text of the email message.
    """
    service = build_gmail_service()
    user_id = 'bestuur@svia.nl'

    msg = MIMEText(render_template(email_template, **kwargs), 'html')
    msg['To'] = to
    msg['From'] = sender
    msg['Subject'] = subject

    body = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

    try:
        email = (service.users().messages().send(userId=user_id, body=body)
                 .execute())
        _logger.info('Sent e-mailmessage Id: %s' % email['id'])
        return email
    except errors.HttpError as e:
        flash('Er is iets mis gegaan met het versturen van de e-mail',
              'danger')
        _logger.warning(e)
        sentry.captureException()
