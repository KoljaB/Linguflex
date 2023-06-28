from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from core import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR

import os.path
import pickle
import googleapiclient.discovery
import pytz
from datetime import datetime, timezone, timedelta

class GoogleCalendarAPI:
    """Eine Klasse zur Interaktion mit der Google Calendar API."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, time_zone='Europe/Berlin', creds_file='credentials.json'):
        """
        Initialisiert das GoogleCalendarAPI-Objekt mit den gegebenen Anmeldeinformationen.
        :param creds_file: Pfad zur Datei mit den Google-Anmeldeinformationen.
        """
        self.time_zone = time_zone
        self.creds_file = creds_file
        self.creds = None
        self.service = None
        self.events_dict = {}
        self.event_counter = 0  # class variable to keep track of custom ids        

    def authenticate(self):
        """
        Authentifiziert den Benutzer und stellt einen Zugriff auf die Google Calendar API her.
        """
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    log(DEBUG_LEVEL_ERR, f'Error refreshing credentials: {str(e)}, please delete token.pickle file')
                    exit(0)                
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
        end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        
        # # get current time in UTC and convert it to local
        # now_utc = datetime.now(pytz.utc)
        # local_now = now_utc.astimezone(self.time_zone)
        # now = local_now.isoformat() + 'Z'

        # # get time 7 days from now in UTC and convert it to local
        # end_utc = now_utc + timedelta(days=7)
        # local_end = end_utc.astimezone(self.time_zone)
        # end = local_end.isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary', timeMin=now, timeMax=end, maxResults=num_events, 
            singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        self.events_dict = {}
        for i, event in enumerate(events):
            # event_id = event['id'][:4]  # get the first four characters of the id
            # self.event_counter += 1  # increment counter
            # custom_id = (event_id + str(self.event_counter)).ljust(5, '_')  # create the custom id
            # #custom_id = str(i+1)  # create shorter, simpler id
            # event['custom_id'] = custom_id  # add the custom id directly to the event object
            # self.events_dict[custom_id] = event  # store event in the dictionary

            self.handle_custom_id(event)            
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            log(DEBUG_LEVEL_MID, f"  [calendar] {start}-{end}: {event['summary']} (ID: {event['id']})")

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
                'timeZone': 'Europe/Berlin',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Berlin',
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
            self.handle_custom_id(event)            
            # event_id = event['id'][:4]  # get the first four characters of the id
            # self.event_counter += 1  # increment counter
            # custom_id = (event_id + str(self.event_counter)).ljust(5, '_')  # create the custom id
            # event['custom_id'] = custom_id  # add the custom id directly to the event object
            # self.events_dict[custom_id] = event  # store event in the dictionary
            log(DEBUG_LEVEL_MID, f"  [calendar] event created: {event.get('htmlLink')}")
            return event
        except Exception as e:
            log(DEBUG_LEVEL_MID, f'  [calendar] error occurred: ' + str(e))
            return None        

        # try:
        #     event = self.service.events().insert(calendarId='primary', body=event).execute()
        #     log(DEBUG_LEVEL_MID, f"  [calendar] event created: {event.get('htmlLink')}")
        #     return event
        # except Exception as e:
        #     log(DEBUG_LEVEL_MID, f'  [calendar] error occurred: ' + str(e))
        #     return None

    def handle_custom_id(self, event):
        """Method to handle custom_id generation"""
        event_id = event['id'][:4]  # get the first four characters of the id
        self.event_counter += 1  # increment counter
        custom_id = (event_id + str(self.event_counter)).ljust(5, '_')  # create the custom id
        event['custom_id'] = custom_id  # add the custom id directly to the event object
        self.events_dict[custom_id] = event  # store event in the dictionary

    def remove_event_by_custom_id(self, custom_id):
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        if custom_id not in self.events_dict:
            log(DEBUG_LEVEL_ERR, f'  [calendar] no event found with id: {custom_id}')
            return

        event = self.events_dict[custom_id]
        self.remove_event(event['id'])   
        return event     

    def remove_event(self, event_id):
        """
        Entfernt ein Ereignis vom primären Kalender des Benutzers hinzu.
        :param event_id: Id des zu löschenden Ereignisses.
        """            
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            log(DEBUG_LEVEL_MID, f"  [calendar] event removed: {event_id}")
        except Exception as e:
            log(DEBUG_LEVEL_MID, f'  [calendar] error occurred: ' + str(e))


    def move_event_by_custom_id(self, custom_id, new_start_time, new_end_time):
        """
        Verschiebt ein Ereignis im primären Kalender des Benutzers an das angegebene Datum und Zeit.
        :param custom_id: Benutzerdefinierte ID des zu bewegenden Ereignisses.
        :param new_start_time: Neue Startzeit des Ereignisses
        :param new_end_time: Neue Endezeit des Ereignisses
        :return: Die verschobene Ereignisinstanz.
        """        
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        if custom_id not in self.events_dict:
            log(DEBUG_LEVEL_MID, f'  [calendar] no event found with id: {custom_id}')
            return

        event = self.events_dict[custom_id]
        return self.move_event(event['id'], new_start_time, new_end_time)


    def move_event(self, event_id, new_start_time, new_end_time):
        """
        Verschiebt ein Ereignis im primären Kalender des Benutzers an das angegebene Datum und Zeit.
        :param event_id: Id des zu löschenden Ereignisses.
        :param new_start_time: Neue Startzeit des Ereignisses
        :param new_end_time: Neue Endezeit des Ereignisses
        :return: Die verschobene Ereignisinstanz.
        """        
        if not self.service:
            log(DEBUG_LEVEL_MID, f'  [calendar] please authenticate first')
            return

        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

            event['start']['dateTime'] = new_start_time.isoformat()
            event['end']['dateTime'] = new_end_time.isoformat()

            updated_event = self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            self.handle_custom_id(updated_event)                 
            
            log(DEBUG_LEVEL_MID, f"  [calendar] event moved: {updated_event.get('htmlLink')}")
            return updated_event
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