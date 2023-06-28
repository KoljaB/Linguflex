from core import ActionModule, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field
import pytz
from google_calendar_helper import GoogleCalendarAPI  
from datetime import datetime, timedelta

time_zone = pytz.timezone(cfg('timezone'))
api = GoogleCalendarAPI()

@linguflex_function
def retrieve_calendar_events():
    "Retrieves current events from the calendar"
    return get_events()


class add_calendar_event(LinguFlexBase):
    "Adds event to the calendar, DO NOT CALL when there is already an event at the add time"
    name: str = Field(..., description="Name or summary")
    date: str = Field(..., description="Date in ISO 8601 format")
    time: str = Field(..., description="Time in 24h format")
    duration: int = Field(..., description="Estimated duration in minutes, pick 30 minutes if you have no better guess")

    def execute(self):
        try:
            start_time_naive = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            start_time_naive = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
        start_time = time_zone.localize(start_time_naive)
        end_time = start_time + timedelta(minutes=self.duration)
        
        event = api.create_event(self.name, start_time, end_time)

        return {"result": "event successfully added to calendar", "id": event["custom_id"]}

class move_calendar_event(LinguFlexBase):
    "Moves event in the calendar, DO NOT CALL when there is already an event at the move time"
    id: str = Field(..., description="Id of the event to move")
    date: str = Field(..., description="Date in ISO 8601 format")
    time: str = Field(..., description="Time in 24h format")
    duration: int = Field(..., description="Estimated duration in minutes, pick 30 minutes if you have no better guess")

    def execute(self):
        try:
            start_time_naive = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            start_time_naive = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
        
        start_time = time_zone.localize(start_time_naive)
        end_time = start_time + timedelta(minutes=self.duration)
        
        event = api.move_event_by_custom_id(self.id, start_time, end_time)

        return {"result": "event successfully moved", "id": event["custom_id"]}

class delete_calendar_event(LinguFlexBase):
    "Deletes event from the calendar"
    id: str = Field(..., description="Id of the event to delete")

    def execute(self):
        event = api.remove_event_by_custom_id(self.id)

        return "event successfully deleted"

def get_events():
    log(DEBUG_LEVEL_MID, f"  [calendar] fetching data")
    api.authenticate()
    calendar_events = api.get_upcoming_events(10)

    events = []
    for calendar_event in calendar_events:
        start = str(calendar_event['start'].get('dateTime', calendar_event['start'].get('date')))
        end = str(calendar_event['end'].get('dateTime', calendar_event['end'].get('date')))
        id = str(calendar_event['custom_id'])
        titel = str(calendar_event['summary'])

        event = {}
        event["Titel"] = titel
        event["Start"] = start
        event["Ende"] = end
        event["Id"] = id
        events.append(event)

    return events

class AddLocalTime(ActionModule):
    def on_function_added(self, message, name, type):         
        self.server.add_time(message)