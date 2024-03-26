"""
Search Module

- performs text and image search using the Google Search API

"""

from lingu import Populatable
from pydantic import Field
from .logic import logic


class RetrieveCalendarEvents(Populatable):
    """
    Retrieves current events from the calendar
    """

    def on_populated(self):
        return logic.get_events()


class AddCalendarEvent(Populatable):
    """
    Adds event to the calendar.
    DO NOT CALL when there is already an event at that time.
    """
    name: str = Field(..., description="Name or summary")
    date: str = Field(..., description="Date in ISO 8601 format")
    time: str = Field(..., description="Time in 24h format")
    duration: int = Field(
        ...,
        description="Estimated duration in minutes. "
        "Pick 30 minutes if you have no better guess.")

    def execute(self):
        return logic.create_calendar_event(
            self.name,
            self.date,
            self.time,
            self.duration)


class MoveCalendarEvent(Populatable):
    """
    Moves event in the calendar.
    DO NOT CALL when there is already an event at the target time.
    """
    id: str = Field(..., description="Id of the event to move")
    date: str = Field(..., description="Date in ISO 8601 format")
    time: str = Field(..., description="Time in 24h format")
    duration: int = Field(
        ...,
        description="Estimated duration in minutes. "
        "Pick 30 minutes if you have no better guess")

    def execute(self):
        return logic.move_calendar_event(
            self.id,
            self.date,
            self.time,
            self.duration)


class DeleteCalendarEvent(Populatable):
    "Deletes event from the calendar"
    id: str = Field(..., description="Id of the event to delete")

    def execute(self):
        return logic.delete_calendar_event(self.id)
