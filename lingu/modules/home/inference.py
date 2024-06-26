"""
Home Assistant Integration Module

- responsible for interacting with Home Assistant via REST API

"""

from lingu import Populatable
from pydantic import Field, conlist, confloat, conint
from typing import Optional, Dict, Any, List
from .logic import logic


class get_states_of_all_devices(Populatable):
    """
    Retrieves the states of all entities in Home Assistant.
    This action fetches the current state of all entities, providing a comprehensive status overview.
    """

    def on_populated(self):
        return logic.get_states()


class turn_on_light(Populatable):
    """
    Turns on a specified light in Home Assistant.
    This action sends a command to turn on the light, which can be used to illuminate a room or area.
    Use correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    light_entity_id: str = Field(..., description="entity_id of the light to turn on. Example: 'light.altar', 'light.couch_unten'")

    def on_populated(self):
        return logic.turn_on_light(self.light_entity_id)


class turn_off_light(Populatable):
    """
    Turns off a specified light in Home Assistant.
    This action sends a command to turn off the light, which can be used to save energy or reduce lighting.
    Use correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    light_entity_id: str = Field(..., description="entity_id of the light to turn off. Example: 'light.altar', 'light.couch_unten'")

    def on_populated(self):
        return logic.turn_off_light(self.light_entity_id)


class turn_on_switch(Populatable):
    """
    Turns on a specified switch in Home Assistant.
    This action sends a command to turn on the switch, which can be used to power a device or outlet.
    Use correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    switch_entity_id: str = Field(..., description="entity_id of the switch to turn on. Example: 'switch.outlet_1', 'switch.living_room_outlet'")

    def on_populated(self):
        return logic.turn_on_switch(self.switch_entity_id)


class turn_off_switch(Populatable):
    """
    Turns off a specified switch in Home Assistant.
    This action sends a command to turn off the switch, which can be used to cut power to a device or outlet.
    Use correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    switch_entity_id: str = Field(..., description="entity_id of the switch to turn off. Example: 'switch.outlet_1', 'switch.living_room_outlet'")

    def on_populated(self):
        return logic.turn_off_switch(self.switch_entity_id)


class set_light_color(Populatable):
    """
    Sets the color of a specified light in Home Assistant.
    This action sends a command to set the color of the light, which can be used to customize the lighting.
    Use the correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    light_entity_id: str = Field(..., description="entity_id of the light to set the color. Example: 'light.altar', 'light.couch_unten'")
    color_name: Optional[str] = Field(None, description="Name of the color to set. Example: 'red', 'blue'")
    # hs_color: Optional[List[conint(ge=0, le=360)]] = Field(None, description="HS color values to set. Example: [300, 70]")
    rgb_color: Optional[List[conint(ge=0, le=255)]] = Field(None, description="RGB color values to set. Example: [255, 0, 0]")

    def on_populated(self):
        return logic.set_light_color(
            self.light_entity_id,
            color_name=self.color_name,
            # hs_color=self.hs_color,
            rgb_color=self.rgb_color
        )


class set_temperature(Populatable):
    """
    Sets the temperature of a specified climate entity in Home Assistant.
    This action sends a command to set the temperature, which can be used to control the climate of a room or area.
    """
    entity_id: str = Field(..., description="entity_id of the climate entity to set the temperature. Example: 'climate.living_room'")
    temperature: float = Field(..., description="Temperature to set. Example: 22.5")

    def on_populated(self):
        return logic.set_temperature(self.entity_id, self.temperature)


class lock(Populatable):
    """
    Locks a specified lock in Home Assistant.
    This action sends a command to lock the lock, which can be used to secure a door or area.
    """
    entity_id: str = Field(..., description="entity_id of the lock to lock. Example: 'lock.front_door'")

    def on_populated(self):
        return logic.lock(self.entity_id)


class unlock(Populatable):
    """
    Unlocks a specified lock in Home Assistant.
    This action sends a command to unlock the lock, which can be used to grant access to a door or area.
    """
    entity_id: str = Field(..., description="entity_id of the lock to unlock. Example: 'lock.front_door'")

    def on_populated(self):
        return logic.unlock(self.entity_id)


class get_config(Populatable):
    """
    Retrieves the current configuration of Home Assistant.
    This action fetches the configuration, providing a comprehensive overview of the system settings.
    """

    def on_populated(self):
        return logic.get_config()


class get_events(Populatable):
    """
    Retrieves the list of events in Home Assistant.
    This action fetches the events, providing an overview of the available events.
    """

    def on_populated(self):
        return logic.get_events()


class get_services(Populatable):
    """
    Retrieves the list of services in Home Assistant.
    This action fetches the services, providing an overview of the available services.
    """

    def on_populated(self):
        return logic.get_services()


class get_history(Populatable):
    """
    Retrieves the history of a specified entity in Home Assistant.
    This action fetches the history, providing an overview of the state changes over a specified period.
    """
    start_time: Optional[str] = Field(None, description="Start time for the history period. Example: '2024-01-01T00:00:00Z'")
    end_time: Optional[str] = Field(None, description="End time for the history period. Example: '2024-01-02T00:00:00Z'")
    filter_entity_id: Optional[str] = Field(None, description="entity_id to filter the history. Example: 'light.altar'")

    def on_populated(self):
        return logic.get_history(start_time=self.start_time, end_time=self.end_time, filter_entity_id=self.filter_entity_id)


class get_logbook(Populatable):
    """
    Retrieves the logbook entries in Home Assistant.
    This action fetches the logbook entries, providing an overview of the events over a specified period.
    """
    start_time: Optional[str] = Field(None, description="Start time for the logbook period. Example: '2024-01-01T00:00:00Z'")
    end_time: Optional[str] = Field(None, description="End time for the logbook period. Example: '2024-01-02T00:00:00Z'")
    entity: Optional[str] = Field(None, description="entity_id to filter the logbook. Example: 'light.altar'")

    def on_populated(self):
        return logic.get_logbook(start_time=self.start_time, end_time=self.end_time, entity=self.entity)


# class get_camera_image(Populatable):
#     """
#     Retrieves the image from a specified camera in Home Assistant.
#     This action fetches the camera image, providing a snapshot from the camera.
#     """
#     entity_id: str = Field(..., description="entity_id of the camera to retrieve the image. Example: 'camera.front_door'")

#     def on_populated(self):
#         return logic.get_camera_image(self.entity_id)


# class get_calendars(Populatable):
#     """
#     Retrieves the list of calendars in Home Assistant.
#     This action fetches the calendars, providing an overview of the available calendars.
#     """

#     def on_populated(self):
#         return logic.get_calendars()


# class get_calendar_events(Populatable):
#     """
#     Retrieves the events from a specified calendar in Home Assistant.
#     This action fetches the calendar events, providing an overview of the scheduled events over a specified period.
#     """
#     calendar_entity_id: str = Field(..., description="entity_id of the calendar to retrieve events from. Example: 'calendar.personal'")
#     start: str = Field(..., description="Start time for the calendar events. Example: '2024-01-01T00:00:00Z'")
#     end: str = Field(..., description="End time for the calendar events. Example: '2024-01-02T00:00:00Z'")

#     def on_populated(self):
#         return logic.get_calendar_events(self.calendar_entity_id, self.start, self.end)


class update_state(Populatable):
    """
    Updates the state of a specified entity in Home Assistant.
    This action sends a command to update the state, which can be used to modify the state of an entity.
    """
    entity_id: str = Field(..., description="entity_id of the entity to update the state. Example: 'light.altar'")
    state: str = Field(..., description="New state to set. Example: 'on'")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Attributes to update. Example: {'brightness': 255}")

    def on_populated(self):
        return logic.update_state(self.entity_id, self.state, self.attributes)


class fire_event(Populatable):
    """
    Fires an event in Home Assistant.
    This action sends a command to fire an event, which can be used to trigger actions based on the event.
    """
    event_type: str = Field(..., description="Type of event to fire. Example: 'custom_event'")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Data for the event. Example: {'key': 'value'}")

    def on_populated(self):
        return logic.fire_event(self.event_type, self.event_data)