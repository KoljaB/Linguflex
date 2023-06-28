from core import BaseModule
from linguflex_functions import LinguFlexBase
from typing import List
from pydantic import Field, BaseModel
from lights_control_helper import LightManager
import os
import enum
import json

class BulbNames(str, enum.Enum):
    "Enumeration representing the names of the available bulbs."

def load_enum_from_strings(data):
    return enum.Enum("BulbNames", {name.replace(" ", "_"): name for name in data}, type=BulbNames)

current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, "lights_control.json")
with open(file_path, "r", encoding='utf-8') as file:
    bulbs = json.load(file)

bulb_names = [item["name"] for item in bulbs]
BulbNames = load_enum_from_strings(bulb_names)

light = LightManager(bulbs)
light.wait_ready() # blocking call

class Bulb(BaseModel):
    "Class representing a bulb, which includes the bulb's name and light color IN HEX (!)."    
    bulb_name: BulbNames = Field(..., description="Name of the bulb")
    color: str = Field(..., description="Color string in hex (eg #FFFFFF)")

class set_bulb_light_color(LinguFlexBase):
    "Sets the hex string(!) colors of the bulbs given in the list."    
    bulbs: List[Bulb] = Field(..., description="List of bulb objects which colors will be set")

    def execute(self):
        for bulb in self.bulbs:
            light.set_color_hex(bulb.bulb_name.value, bulb.color)
        return "light colors successfully set"
    
class ShutdownHandler(BaseModule):    
    def shutdown(self) -> None:
        light.shutdown()    