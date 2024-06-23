"""
Home Assistant Integration Module

- responsible for interacting with Home Assistant via REST API

"""

from lingu import Populatable
from pydantic import Field, conlist, confloat
from typing import Optional, List
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


class set_light_color(Populatable):
    """
    Sets the color of a specified light in Home Assistant.
    This action sends a command to set the color of the light, which can be used to customize the lighting.
    Use the correct entity_id.
    Call get_states_of_all_devices first if you are unsure.
    """
    light_entity_id: str = Field(..., description="entity_id of the light to set the color. Example: 'light.altar', 'light.couch_unten'")
    color_name: Optional[str] = Field(None, description="Name of the color to set. Example: 'red', 'blue'")
    hs_color: Optional[conlist(confloat(ge=0, le=360), min_length=2, max_length=2)] = Field(None, description="HS color values to set. Example: [300, 70]")
    rgb_color: Optional[conlist(confloat(ge=0, le=255), min_length=3, max_length=3)] = Field(None, description="RGB color values to set. Example: [255, 0, 0]")

    def on_populated(self):
        return logic.set_light_color(
            self.light_entity_id,
            color_name=self.color_name,
            hs_color=self.hs_color,
            rgb_color=self.rgb_color
        )