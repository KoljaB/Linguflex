from .handlers.google_calendar import GoogleCalendarAPI
from datetime import datetime, timedelta
from lingu import log, cfg, Logic
import pytz
import os
cfg_time_zone = cfg("timezone", default="Europe/Berlin")
credentials_file_path = cfg(
    "calendar",
    "credentials_file_path",
    default="credentials.json")
time_zone = pytz.timezone(cfg_time_zone)
no_cred_msg = "Can't perform that action, "
"Google Calendar API credentials file is needed."


class CalendarLogic(Logic):
    """
    Logic class for the Calendar module.
    """
    def init(self):
        """Initializes the CalendarLogic class."""
        self.calendar = GoogleCalendarAPI()

        credentials_json_file_exists = os.path.exists(credentials_file_path)
        if not credentials_json_file_exists:
            log.err(
                "[calendar] Missing Google Calendar API credentials file.\n"
                "  Create a project at https://console.developers.google.com/"
                " and enable the Google Calendar API.\n"
                "  Download the credentials.json file and place it in the"
                " executing directory of Linguflex."
            )
            self.state.set_disabled(True)
        else:
            self.calendar = GoogleCalendarAPI()

        self.ready()

    def get_events(self, num_events=10):
        """
        Gets the upcoming events from the Google Calendar API.

        Args:
            num_events (int): The number of upcoming events to get.

        Returns:
            dict: The upcoming events.
        """
        if not self.calendar:
            return no_cred_msg

        log.inf("  [calendar] getting events")
        self.calendar.authenticate()
        calendar_events = self.calendar.get_upcoming_events(10)

        events = []
        for calendar_event in calendar_events:
            start = str(calendar_event['start'].get(
                'dateTime', calendar_event['start'].get('date')))
            end = str(calendar_event['end'].get(
                'dateTime', calendar_event['end'].get('date')))
            id = str(calendar_event['custom_id'])
            titel = str(calendar_event['summary'])

            event = {}
            event["Titel"] = titel
            event["Start"] = start
            event["Ende"] = end
            event["Id"] = id

            events.append(event)

            if len(events) >= num_events:
                break

        return events

    def create_calendar_event(self, name, date, time, duration):
        """
        Creates a new event in the Google Calendar API.

        Args:
            name (str): The name or summary of the event.
            date (str): The date of the event in ISO 8601 format.
            time (str): The time of the event in 24h format.
            duration (int): The estimated duration of the event in minutes.

        Returns:
            dict: The created event.
        """
        if not self.calendar:
            return no_cred_msg

        log.inf("  [calendar] creating event")

        try:
            self.calendar.authenticate()
            start_time_naive = datetime.strptime(
                f"{date} {time}", "%Y-%m-%d %H:%M:%S")
            start_time = time_zone.localize(start_time_naive)
            end_time = start_time + timedelta(minutes=duration)

            event = self.calendar.create_event(name, start_time, end_time)
        except Exception as e:
            log.err(f"  [calendar] error creating event: {e}")
            return {
                "result": "error creating event",
                "error": str(e)
            }

        return {
            "result": "event successfully added to calendar",
            "id": event["custom_id"]
        }

    def move_calendar_event(self, event_id, date, time, duration):
        """
        Moves an event in the Google Calendar API.

        Args:
            event_id (str): The ID of the event to move.
            date (str): The date of the event in ISO 8601 format.
            time (str): The time of the event in 24h format.
            duration (int): The estimated duration of the event in minutes.

        Returns:
            dict: The moved event.
        """
        if not self.calendar:
            return no_cred_msg

        log.inf("  [calendar] moving event")

        try:
            self.calendar.authenticate()
            start_time_naive = datetime.strptime(
                f"{date} {time}", "%Y-%m-%d %H:%M:%S")
            start_time = time_zone.localize(start_time_naive)
            end_time = start_time + timedelta(minutes=duration)

            event = self.calendar.move_event_by_custom_id(
                event_id, start_time, end_time)
        except Exception as e:
            log.err(f"  [calendar] error moving event: {e}")
            return {
                "result": "error moving event",
                "error": str(e)
            }

        return {
            "result": "event successfully moved",
            "id": event["custom_id"]
        }

    def delete_calendar_event(self, event_id):
        """
        Deletes an event in the Google Calendar API.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            dict: The deleted event.
        """
        if not self.calendar:
            return no_cred_msg

        log.inf("  [calendar] deleting event")

        try:
            self.calendar.authenticate()
            event = self.calendar.remove_event_by_custom_id(event_id)
        except Exception as e:
            log.err(f"  [calendar] error deleting event: {e}")
            return {
                "result": "error deleting event",
                "error": str(e)
            }

        return {
            "result": "event successfully deleted",
            "id": event["custom_id"]
        }


logic = CalendarLogic()
