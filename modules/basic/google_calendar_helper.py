from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX

import os.path
import pickle
import googleapiclient.discovery
from datetime import datetime, timezone

class GoogleCalendarAPI:
    """Eine Klasse zur Interaktion mit der Google Calendar API."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, creds_file='credentials.json'):
        """
        Initialisiert das GoogleCalendarAPI-Objekt mit den gegebenen Anmeldeinformationen.
        :param creds_file: Pfad zur Datei mit den Google-Anmeldeinformationen.
        """
        self.creds_file = creds_file
        self.creds = None
        self.service = None

    def authenticate(self):
        """
        Authentifiziert den Benutzer und stellt einen Zugriff auf die Google Calendar API her.
        """
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # save creds for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=self.creds)

    def get_upcoming_events(self, num_events=10):
        """
        Gibt die nächsten Ereignisse aus dem primären Kalender des Benutzers zurück.
        :param num_events: Anzahl der abzurufenden Ereignisse.
        :return: Liste der nächsten Ereignisse.
        """
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId='primary', timeMin=now, maxResults=num_events, 
            singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    
    def create_event(self, summary, start_time, end_time):
        """
        Creates a new event with the given summary, start time, and end time.
        :param summary: The summary (or title) of the event.
        :param start_time: The start time of the event.
        :param end_time: The end time of the event.
        :return: The created event instance.
        """
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            }
        }

        return self.add_event(event)    
    
    def add_event(self, event):
        """
        Fügt ein Ereignis zum primären Kalender des Benutzers hinzu.
        :param event: Ein Dictionary, das die Eventdetails repräsentiert.
        :return: Die erstellte Ereignisinstanz.
        """
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            log(DEBUG_LEVEL_MID, f"  [calendar] event created: {event.get('htmlLink')}")
            return event
        except Exception as e:
            log(DEBUG_LEVEL_MID, f'  [calendar] error occurred: ' + str(e))
            return None

"""

The dictionary for add_event should be in the following format:

event = {
  'summary': 'My demo Meeting',
  'start': {
    'dateTime': '2023-06-01T12:00:00+01:00',
  },
  'end': {
    'dateTime': '2023-06-01T13:00:00+01:00',
  }
}

event = {
  'summary': 'Google I/O 2025',
  'location': '800 Howard St., San Francisco, CA 94103',
  'description': 'A chance to learn about Google\'s latest developer products.',
  'start': {
    'dateTime': '2025-05-28T09:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2025-05-28T17:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'attendees': [
    {'email': 'lpage@example.com'},
    {'email': 'sbrin@example.com'},
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}

"""