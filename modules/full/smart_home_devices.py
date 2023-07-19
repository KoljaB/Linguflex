from core import BaseModule, Request
from linguflex_functions import LinguFlexBase
from typing import List
from pydantic import Field, BaseModel
from smart_home_devices_helper import LightManager, OutletManager
import os
import enum
import json

# file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_home_devices.json")
file_path = "config/smart_home_devices.json"
with open(file_path, "r", encoding='utf-8') as file:
    devices = json.load(file)


light = LightManager([d for d in devices if d["type"] == "Bulb"])
light.wait_ready() # blocking call

bulb_names = [d["name"].replace(" ", "_") for d in devices if d["type"] == "Bulb"]
bulb_names_string = ', '.join(bulb_names)

class Bulb(BaseModel):
    "Represents a bulb with name and color"    
    name: str = Field(..., description="Bulb name")
    color: str = Field(..., description="Hexadezimal color string (#FF00FF for example)")

class set_bulb_light_color(LinguFlexBase):
    "Sets color of bulbs. Use hex string for color. Example: use #FF0000 instead of red."
    bulbs: List[Bulb] = Field(..., description=f"List of bulbs: {bulb_names_string}")

    def execute(self):
        retval = {
            "result": "error",
            "reason" : "no bulbs in list",
        }
        for bulb in self.bulbs:
            retval = light.set_color_hex(bulb.name, bulb.color)
            if retval["result"] != "success":
                return retval
        light.raise_color_information_event()
        return retval
    
class get_bulb_light_colors(LinguFlexBase):
    "Retrieves the hex string colors of the bulbs."

    def execute(self):
        return light.get_colors_json_hex()


smartplug = OutletManager([d for d in devices if d["type"] == "Outlet"])
smartplug_names = [d["name"].replace(" ", "_") for d in devices if d["type"] == "Outlet"]
smartplug_names_string = ','.join(smartplug_names)
device_names_string = ', '.join(bulb_names + smartplug_names)

class set_smart_device_on_off(LinguFlexBase):
    "Turn smart devices with given name on (True) or off (False)."
    name: str = Field(..., description=f"Name of smart device to turn on or off, MUST be one of these: {device_names_string}")
    turn_on: bool = Field(..., description="True = on, False = off")

    def execute(self):
        # Check if device is a bulb
        if self.name in bulb_names:
            return light.set_bulb_on_off(self.name, self.turn_on)
        else:
            return smartplug.set_state(self.name, self.turn_on)
    
class get_smart_device_on_off_state(LinguFlexBase):
    "Returns on/off state of smart devices with given name."
    name: str = Field(..., description=f"Name of smart device to retrieve state from, MUST be one of these: {smartplug_names_string}")

    def execute(self):
        # Check if device is a bulb
        if self.name in bulb_names:
            return light.get_bulb_on_off_state(self.name)
        else:
            return smartplug.get_state(self.name)


class ShutdownHandler(BaseModule):    
    def init(self):
        light.server = self.server
        light.raise_color_information_event()

    def on_function_added(self, 
            request: Request,
            function_name: str,
            caller_name: str,
            type: str) -> None: 
        
        # if we added a function from this module (meaning we reacted to any keywords)
        if self.name == caller_name:
            color = light.get_colors_json_hex()
            request.add_prompt(f"Bulb colors: {color}")

    def shutdown(self):
        light.shutdown()    
        smartplug.shutdown()