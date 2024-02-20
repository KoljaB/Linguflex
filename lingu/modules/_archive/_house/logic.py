from .handlers.smart_home_devices_helper import LightManager, OutletManager
from .handlers.wled import WLED_Handler
from lingu import log, Level, LogicBase, cfg
from .state import state
import threading
import json

CONFIG_FILE_PATH = "config/smart_home_devices.json"

class HouseLogic(LogicBase):
    def __init__(self):
        super().__init__()        
        self.light = None
        self.outlet = None
        self.lights_ready = False
        
        log(Level.Dbg, f"  [lights] reading devices")
        with open(CONFIG_FILE_PATH, "r", encoding='utf-8') as file:
            self.devices = json.load(file)
        log(Level.Dbg, f"  [lights] devices: {self.devices}")

        self.wled_url = cfg('wled_url', section="wled")
        self.max_bulbs = int(cfg('max_bulbs', 300, section="wled"))

        self.bulb_names = [d["name"].replace(" ", "_") for d in self.devices if d["type"] == "Bulb"]
        self.bulb_names_string = ', '.join(self.bulb_names)

        self.outlet_names = [d["name"].replace(" ", "_") for d in self.devices if d["type"] == "Outlet"]
        self.outlet_names_string = ','.join(self.outlet_names)

        self.all_devices_names_string = ', '.join(self.bulb_names + self.outlet_names)

    def wait_for_lights(self):
        log(Level.Dbg, f"  [lights] waiting for lights state")
        self.light.wait_ready()
        log(Level.Info, f"  [lights] lights ready")
        self.lights_ready = True
        self.colors_changed()

    def init(self):        
        log(Level.Info, f"  [lights] starting light manager")
        self.light = LightManager([d for d in self.devices if d["type"] == "Bulb"])
        threading.Thread(target=self.wait_for_lights).start()
        self.outlet = OutletManager([d for d in self.devices if d["type"] == "Outlet"])
        self.wled = WLED_Handler(self.wled_url, self.max_bulbs)

    def get_bulb_names(self):
        return self.bulb_names

    def get_bulb_names_string(self):
        return self.bulb_names_string
    
    def set_bulb_on_off(self, bulb_name, state):
        return self.light.set_bulb_on_off(bulb_name, state)
    
    def get_bulb_on_off_state(self, bulb_name):
        return self.light.get_bulb_on_off_state(bulb_name)
    
    def set_color_hex(self, bulb_name, color_string):
        self.light.set_color_hex(bulb_name, color_string)

    def get_colors_json_hex(self):
        return self.light.get_colors_json_hex()


    def get_outlet_names(self):
        return self.outlet_names

    def get_outlet_names_string(self):
        return self.outlet_names_string

    def set_outlet_on_off(self, outlet_name, state):
        return self.outlet.set_state(outlet_name, state)
    
    def get_outlet_on_off_state(self, outlet_name):
        return self.outlet.get_state(outlet_name)


    def colors_changed(self):
        print ("  [lights] calling light.get_colors()")
        self.light.get_colors()
        print ("  [lights] calling wled.bulb_colors_changed()")
        colors = self.light.get_colors_json_rgb()
        print ("  [lights] calling wled.bulb_colors_changed()")
        self.wled.bulb_colors_changed(colors)
        print ("  [lights] finished colors_changed()")

logic = HouseLogic()