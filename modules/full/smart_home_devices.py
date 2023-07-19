from core import BaseModule, Request, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
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
        result = {}
        for bulb in self.bulbs:
            # Check if device is a bulb
            if bulb.name in bulb_names:
                log(DEBUG_LEVEL_MAX, f'  [lights] {bulb.name} initiating color set to: {bulb.color}')
                result[bulb.name] = light.set_color_hex(bulb.name, bulb.color)
            else:
                log(DEBUG_LEVEL_MAX, f'  [lights] {bulb.name} not found {bulb.color}')        
                result[bulb.name] = {
                "result": "error",
                "reason" : f"bulb name {bulb.name} not found, must be one of these: {bulb_names_string}",
            }
        light.raise_color_information_event()
        return result

        # retval = {
        #     "result": "error",
        #     "reason" : "no bulbs in list",
        # }
        # for bulb in self.bulbs:
        #     retval = light.set_color_hex(bulb.name, bulb.color)
        #     if retval["result"] != "success":
        #         return retval
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
    "Turn smart devices or lamps with given names on (True) or off (False)."
    names: List[str] = Field(..., description=f"Names of smart devices to turn on or off, MUST be one of these: {device_names_string}")
    turn_on: bool = Field(..., description="True = on, False = off")

    def execute(self):
        result = {}
        for name in self.names:
            # Check if device is a bulb
            if name in bulb_names:
                result[name] = light.set_bulb_on_off(name, self.turn_on)
            elif name in smartplug_names:
                result[name] = smartplug.set_state(name, self.turn_on)
            else:
                result[name] = {
                "result": "error",
                "reason" : f"device name {name} not found, must be one of these: {device_names_string}",
            }
        return result
    
class get_smart_device_on_off_state(LinguFlexBase):
    "Returns on/off state of smart devices or lamps with given names."
    names: List[str] = Field(..., description=f"Names of smart devices to retrieve state from, MUST be one of these: {smartplug_names_string}")

    def execute(self):
        result = {}
        for name in self.names:
            # Check if device is a bulb
            if name in bulb_names:
                result[name] = light.get_bulb_on_off_state(name)
            else:
                result[name] = smartplug.get_state(name)
        return result



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