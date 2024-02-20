"""
House / Smart Home Module

- responsible for turning devices on and off and setting colors of bulbs

"""

from lingu import log, Invokable, Populatable
from pydantic import BaseModel, Field
from .logic import logic
from typing import List


class Bulb(BaseModel):
    "Represents a bulb with name and color"
    name: str = Field(
        ...,
        description="Permitted (allowed) bulb names: "
                    f"{logic.get_bulb_names()}"
    )
    color: str = Field(..., description="MUST be hex string! Example: #FF00FF")


class set_bulb_light_color(Populatable):
    """
    The task is to set the color of light bulbs. To do this, you need to:

    1. Compare the names of the bulbs you have been requested to change with a list of allowed bulb names.
    2. Select the allowed bulb names that best match the requested ones.
    3. Ensure you only submit the names of bulbs that are permitted (allowed).
    4. Specify the color for each bulb using a hex color code (e.g., #FF0000) rather than color names (like "red").
    """
    bulbs: List[Bulb] = Field(
        ...,
        description="List of bulbs. "
                    f"Permitted (allowed) bulb names: {logic.get_bulb_names()}")

    def on_populated(self):
        result = {}
        for bulb in self.bulbs:
            if bulb.name in logic.get_bulb_names():
                log.dbg(f'  [lights] {bulb.name} to {bulb.color}')
                result[bulb.name] = logic.set_color_hex(bulb.name, bulb.color)
            else:
                log.dbg(f'  [lights] {bulb.name} not found {bulb.color}')
                result[bulb.name] = {
                    "result": "error",
                    "reason": f"bulb name {bulb.name} not found, "
                              "must be one of these: "
                              f"{logic.get_bulb_names_string()}",
                }

        logic.colors_changed()
        return result


@Invokable
def get_bulb_light_colors():
    """
    Only call if you really need to know the current colors of the bulbs.
    Call set_bulb_light_color instead if asked to set colors.
    """

    return logic.get_colors_json_hex()


class set_smart_device_on_off(Populatable):
    "Turn smart devices or lamps with given names on (True) or off (False)."
    names: List[str] = Field(
        ...,
        description="MUST ONLY be from this list: "
                    f"{logic.get_outlet_names_string()}"
    )
    turn_on: bool = Field(..., description="True = on, False = off")

    def on_populated(self):
        result = {}
        bulb_state_changed = False
        for name in self.names:
            # Check if device is a bulb
            if name in logic.get_bulb_names():
                bulb_state_changed = True
                result[name] = logic.set_bulb_on_off(name, self.turn_on)
            elif name in logic.get_outlet_names():
                result[name] = logic.set_outlet_on_off(name, self.turn_on)

            else:
                print(f"  [lights] {name} not found")
                print(f"  [lights] bulbs: {logic.get_bulb_names()}")
                print(f"  [lights] outlets: {logic.get_outlet_names()}")
                result[name] = {
                    "result": "error",
                    "reason": f"device name {name} not found, "
                              "must be one of these: "
                              f"{logic.get_outlet_names_string()}",
                }
        if bulb_state_changed:
            logic.colors_changed()
        return result


class get_smart_device_on_off_state(Populatable):
    "Returns on/off state of smart devices or lamps with given names."
    names: List[str] = Field(
        ...,
        description="MUST ONLY be from this list: "
                    f"{logic.get_outlet_names_string()}"
    )

    def on_populated(self):
        result = {}
        for name in self.names:
            # Check if device is a bulb
            if name in logic.get_bulb_names():
                result[name] = logic.get_bulb_on_off_state(name)
            else:
                result[name] = logic.get_outlet_on_off_state(name)
        return result
