"""
Home Assistant Integration Module

- responsible for interacting with Home Assistant via REST API

"""

from lingu import Populatable
from pydantic import Field
from .logic import logic


class get_states_of_all_home_assistant_devices(Populatable):
    """
    Retrieves the states of all entities in Home Assistant.
    This action fetches the current state of all entities, providing a comprehensive status overview.
    """

    def on_populated(self):
        return logic.get_states()


# class turn_on_home_assistant_light(Populatable):
#     """
#     Turns on a specified light in Home Assistant.
#     This action sends a command to turn on the light, which can be used to illuminate a room or area.
#     """
#     light_name: str = Field(..., description="Name of the light to turn on. Example: 'living_room_light', 'bedroom_lamp'")

#     def on_populated(self):
#         return logic.turn_on_light(self.light_name)


# class turn_off_home_assistant_light(Populatable):
#     """
#     Turns off a specified light in Home Assistant.
#     This action sends a command to turn off the light, which can be used to darken a room or area, saving energy.
#     """
#     light_name: str = Field(..., description="Name of the light to turn off. Example: 'living_room_light', 'bedroom_lamp'")

#     def on_populated(self):
#         return logic.turn_off_light(self.light_name)


# class set_home_assistant_light_color(Populatable):
#     """
#     Sets the color of a specified light in Home Assistant.
#     This action changes the light color to the specified hex value (e.g., #FF00FF for purple), allowing for ambiance control.
#     """
#     light_name: str = Field(..., description="Name of the light to set color for. Example: 'living_room_light', 'bedroom_lamp'")
#     color: str = Field(..., description="Color to set in hex format (e.g., #FF00FF).")

#     def on_populated(self):
#         return logic.set_light_color(self.light_name, self.color)


# class turn_on_home_assistant_device(Populatable):
#     """
#     Turns on a specified smart device in Home Assistant.
#     This action sends a command to power on the device, which could be anything from a smart plug to a fan.
#     """
#     device_name: str = Field(..., description="Name of the device to turn on. Example: 'living_room_fan', 'kitchen_smart_plug'")

#     def on_populated(self):
#         return logic.turn_on_device(self.device_name)


# class turn_off_home_assistant_device(Populatable):
#     """
#     Turns off a specified smart device in Home Assistant.
#     This action sends a command to power off the device, helping to conserve energy or stop the device from operating.
#     """
#     device_name: str = Field(..., description="Name of the device to turn off. Example: 'living_room_fan', 'kitchen_smart_plug'")

#     def on_populated(self):
#         return logic.turn_off_device(self.device_name)


# class get_home_assistant_device_state(Populatable):
#     """
#     Retrieves the state of a specified smart device in Home Assistant.
#     This action gets the current status of the device, such as whether it is on or off, allowing for status checks.
#     """
#     device_name: str = Field(..., description="Name of the device to get state for. Example: 'living_room_fan', 'kitchen_smart_plug'")

#     def on_populated(self):
#         return logic.get_device_state(self.device_name)


# class get_home_assistant_sensor_state(Populatable):
#     """
#     Retrieves the state of a specified sensor in Home Assistant.
#     This action gets the current readings from sensors like temperature, humidity, or motion, providing real-time data.
#     """
#     sensor_name: str = Field(..., description="Name of the sensor to get state for. Example: 'living_room_temperature', 'bedroom_motion_sensor'")

#     def on_populated(self):
#         return logic.get_sensor_state(self.sensor_name)


# class trigger_home_assistant_automation(Populatable):
#     """
#     Triggers a specified automation in Home Assistant.
#     This action starts a predefined sequence of actions (an automation), such as turning on lights when motion is detected.
#     """
#     automation_name: str = Field(..., description="Name of the automation to trigger. Example: 'morning_routine', 'night_security'")

#     def on_populated(self):
#         return logic.trigger_automation(self.automation_name)


# class activate_home_assistant_scene(Populatable):
#     """
#     Activates a specified scene in Home Assistant.
#     This action sets multiple devices to predefined states, creating a specific environment, such as a 'movie night' scene.
#     """
#     scene_name: str = Field(..., description="Name of the scene to activate. Example: 'movie_night', 'romantic_dinner'")

#     def on_populated(self):
#         return logic.activate_scene(self.scene_name)


# class set_home_assistant_thermostat_temperature(Populatable):
#     """
#     Sets the temperature of a specified thermostat in Home Assistant.
#     This action adjusts the thermostat to a desired temperature, helping to control the climate of a room or area.
#     """
#     thermostat_name: str = Field(..., description="Name of the thermostat to set temperature for. Example: 'living_room_thermostat', 'bedroom_thermostat'")
#     temperature: float = Field(..., description="Temperature to set in degrees. Example: 22.5")

#     def on_populated(self):
#         return logic.set_thermostat_temperature(self.thermostat_name, self.temperature)


# class lock_home_assistant_device(Populatable):
#     """
#     Locks a specified lock in Home Assistant.
#     This action sends a command to lock the device, which could be a door lock, enhancing security.
#     """
#     lock_name: str = Field(..., description="Name of the lock to lock. Example: 'front_door_lock', 'garage_door_lock'")

#     def on_populated(self):
#         return logic.lock_device(self.lock_name)


# class unlock_home_assistant_device(Populatable):
#     """
#     Unlocks a specified lock in Home Assistant.
#     This action sends a command to unlock the device, such as a door lock, providing access to a secured area.
#     """
#     lock_name: str = Field(..., description="Name of the lock to unlock. Example: 'front_door_lock', 'garage_door_lock'")

#     def on_populated(self):
#         return logic.unlock_device(self.lock_name)


# class open_home_assistant_cover(Populatable):
#     """
#     Opens a specified cover in Home Assistant.
#     This action sends a command to open covers like blinds, curtains, or garage doors, allowing light in or access to an area.
#     """
#     cover_name: str = Field(..., description="Name of the cover to open. Example: 'living_room_blinds', 'garage_door'")

#     def on_populated(self):
#         return logic.open_cover(self.cover_name)


# class close_home_assistant_cover(Populatable):
#     """
#     Closes a specified cover in Home Assistant.
#     This action sends a command to close covers like blinds, curtains, or garage doors, providing privacy or security.
#     """
#     cover_name: str = Field(..., description="Name of the cover to close. Example: 'living_room_blinds', 'garage_door'")

#     def on_populated(self):
#         return logic.close_cover(self.cover_name)

