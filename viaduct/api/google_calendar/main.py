import argparse
import os
import sys

from httplib2 import Http
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is the OAuth 2.0 info with client_id and client_secret
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=['https://www.googleapis.com/auth/calendar']
)

# google calendar Settings > via_events > id 
via_calendar_id = 'bka8j77cis5ffr2pokn5ef5cso@group.calendar.google.com'


def auth(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # credentials will get written back to the file.
    storage = file.Storage('token.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    # httplib2.Http for authorized request with OAUTH credentials.
    http = Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    return discovery.build('calendar', 'v3', http=http)

# Lists events for testing
def list(service):
    events = service.events() \
            .list(calendarId=via_calendar_id, maxResults=2) \
            .execute()
    
    print events
    
def insert(service):
    # Event to insert
    event = {
      'summary': 'ICT test event : Als je dit ziet moet je oeloeloeh roepen',
      'location': 'Via kamer',
      'start': {
        'dateTime': '2014-03-10T14:00:00.000-00:00'
      },
      'end': {
        'dateTime': '2014-03-10T15:00:00.000-00:00'
      }
    }

  
    event = service.events() \
            .insert(calendarId=via_calendar_id, body=event) \
            .execute()
        
    print event

if __name__ == '__main__':
  service = auth(sys.argv)
  
  list(service)