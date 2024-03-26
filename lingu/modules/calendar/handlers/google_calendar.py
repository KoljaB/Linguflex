from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import googleapiclient.discovery
from lingu import log
from datetime import datetime, timedelta

TOKEN_FILE = "token.pickle"


class GoogleCalendarAPI:
    """A class for interacting with the Google Calendar API."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(
            self,
            time_zone="Europe/Berlin",
            creds_file="credentials.json"):
        """
        Initializes the GoogleCalendarAPI object with the given credentials.
        :param creds_file: Path to the file with Google credentials.
        """
        self.time_zone = time_zone
        self.creds_file = creds_file
        self.creds = None
        self.service = None
        self.events_dict = {}
        self.event_counter = 0

    def authenticate(self):
        """
        Authenticates the user and establishes
          access to the Google Calendar API.
        """
        # Check if token file exists and load it
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)

        # Refresh or create new credentials if necessary
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    log.err(f"  [calendar] {e}")
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    self.creds = None
                    raise Exception(
                        "ERROR: Token file expired, file was deleted."
                        " Try ONE TIME again.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save credentials for the next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)

        # Create Google Calendar service
        self.service = googleapiclient.discovery.build(
            "calendar",
            "v3",
            credentials=self.creds)

    def get_upcoming_events(self, num_events=10):
        """
        Returns the next events from the user's primary calendar.
        :param num_events: Number of events to retrieve.
        :return: List of upcoming events.
        """
        if not self.service:
            log.inf("  [calendar] please authenticate first")
            return

        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=num_events,
            singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        self.events_dict = {}
        for i, event in enumerate(events):
            self.handle_custom_id(event)

            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            log.inf(f"  [calendar] {start}-{end}: {event['summary']}"
                     f" (ID: {event['id']})")

        return events

    def handle_custom_id(self, event):
        """Method to handle custom_id generation."""
        event_id = event['id'][:4]
        self.event_counter += 1

        # Create the custom id
        custom_id = (event_id + str(self.event_counter)).ljust(5, '_')

        event['custom_id'] = custom_id
        self.events_dict[custom_id] = event

    def create_event(self, summary, start_time, end_time):
        """
        Creates a new event with the given summary, start time, and end time.
        :param summary: The summary (or title) of the event.
        :param start_time: The start time of the event.
        :param end_time: The end time of the event.
        :return: The created event instance.
        """
        if not self.service:
            log.inf("  [calendar] please authenticate first")
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
        Adds an event to the user's primary calendar.
        :param event: A dictionary representing the event details.
        :return: The created event instance.
        """
        if not self.service:
            log.inf("  [calendar] please authenticate first")
            return

        try:
            event = self.service.events().insert(
                calendarId="primary",
                body=event).execute()
            self.handle_custom_id(event)
            log.inf(f"  [calendar] event created: {event.get('htmlLink')}")
            return event
        except Exception as e:
            log.inf('  [calendar] error occurred: ' + str(e))
            return None

    def remove_event_by_custom_id(self, custom_id):
        """
        Removes an event from the primary calendar of the user by a custom ID.
        :param custom_id: Custom ID of the event to be removed.
        """
        if not self.service:
            log.inf('  [calendar] please authenticate first')
            return

        if custom_id not in self.events_dict:
            log.err(f'  [calendar] no event found with id: {custom_id}')
            return

        event = self.events_dict[custom_id]
        self.remove_event(event['id'])
        return event

    def remove_event(self, event_id):
        """
        Removes an event from the primary calendar of the user.
        :param event_id: ID of the event to be removed.
        """
        if not self.service:
            log.inf('  [calendar] please authenticate first')
            return

        try:
            self.service.events().delete(
                calendarId="primary",
                eventId=event_id).execute()
            log.inf(f"  [calendar] event removed: {event_id}")
        except Exception as e:
            log.err('  [calendar] error occurred: ' + str(e))

    def move_event_by_custom_id(self, custom_id, new_start_time, new_end_time):
        """
        Moves an event in the primary calendar of the user to the
          specified date and time.
        :param custom_id: Custom ID of the event to be moved.
        :param new_start_time: New start time of the event.
        :param new_end_time: New end time of the event.
        :return: The moved event instance.
        """
        if not self.service:
            log.inf('  [calendar] please authenticate first')
            return

        if custom_id not in self.events_dict:
            log.inf(f'  [calendar] no event found with id: {custom_id}')
            return

        event = self.events_dict[custom_id]
        return self.move_event(event['id'], new_start_time, new_end_time)

    def move_event(self, event_id, new_start_time, new_end_time):
        """
        Moves an event in the primary calendar of the user to the
          specified date and time.
        :param event_id: ID of the event to be moved.
        :param new_start_time: New start time of the event.
        :param new_end_time: New end time of the event.
        :return: The moved event instance.
        """
        if not self.service:
            log.inf('  [calendar] please authenticate first')
            return

        try:
            event = self.service.events().get(
                calendarId="primary",
                eventId=event_id).execute()

            event['start']['dateTime'] = new_start_time.isoformat()
            event['end']['dateTime'] = new_end_time.isoformat()

            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event).execute()
            self.handle_custom_id(updated_event)

            log.inf("  [calendar] event moved:"
                    f" {updated_event.get('htmlLink')}")
            return updated_event
        except Exception as e:
            log.err('  [calendar] error occurred: ' + str(e))
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
  'description': 'A chance to learn about latest developer products.',
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
