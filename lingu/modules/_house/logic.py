from .handlers.smart_home_devices_helper import LightManager, OutletManager
from .handlers.wled import WLED_Handler
from lingu import log, cfg, Logic
import threading
import json

CONFIG_FILE_PATH = "lingu/config/smart_home_devices.json"


class HouseLogic(Logic):
    def __init__(self):
        super().__init__()
        self.light = None
        self.outlet = None
        self.lights_ready = False
        self.outlets_ready = False
        self.bulb_states = {}
        self.outlet_states = {}

        log.dbg(f"  [house] reading devices from {CONFIG_FILE_PATH}")
        with open(CONFIG_FILE_PATH, "r", encoding='utf-8') as file:
            self.devices = json.load(file)

        log.dbg(f"  [house] devices: {self.devices}")

        self.wled_url = cfg("wled", "wled_url")
        self.max_bulbs = int(cfg("wled", "max_bulbs", default=300))

        self.bulb_names = [
            d["name"].replace(" ", "_")
            for d in self.devices
            if d["type"] == "Bulb"
        ]
        self.bulb_names_string = ', '.join(self.bulb_names)

        self.outlet_names = [
            d["name"].replace(" ", "_")
            for d in self.devices
            if d["type"] == "Outlet"
        ]
        self.outlet_names_string = ', '.join(self.outlet_names)

        self.all_devices_names_string = ', '.join(
            self.bulb_names + self.outlet_names
        )

    def wait_for_lights(self):
        log.dbg("  [house] waiting for lights and outlets to be ready")
        self.light.wait_ready()
        self.lights_ready = True
        log.dbg("  [house] lights ready")
        # self.outlet.wait_ready()
        self.outlets_ready = True
        # log.dbg("  [house] outlet ready")
        self.colors_changed()
        self.ready()

    def init(self):
        log.inf("  [house] initializing")
        self.light = LightManager([
            d for d in self.devices
            if d["type"] == "Bulb"
        ])
        threading.Thread(target=self.wait_for_lights).start()
        self.outlet = OutletManager([
            d for d in self.devices
            if d["type"] == "Outlet"
        ])
        self.wled = WLED_Handler(self.wled_url, self.max_bulbs)

    def trigger_states(self):
        if self.lights_ready:
            self.bulb_states = self._fetch_bulb_states()
            # self.trigger("bulb_states", bulb_states)

        if self.outlets_ready:
            self.outlet_states = self._fetch_outlet_states()
            # self.trigger("outlet_states", outlet_states)

        self.trigger("states_ready")

    def set_color_hex(self, bulb_name, color_string):
        return self.light.set_color_hex(bulb_name, color_string)

    def _fetch_bulb_states(self):
        bulb_states = {}
        for bulb_name in self.bulb_names:
            on_off = self.light.get_bulb_on_off_state(bulb_name)
            color = self.light.get_color(bulb_name)
            is_on = on_off["state"] == "on"
            bulb_states[bulb_name] = {
                "is_on": is_on,
                "color": color
            }
        return bulb_states

    def _fetch_outlet_states(self):
        outlet_states = {}
        for outlet_name in self.outlet_names:
            is_on = self.outlet.get_state(outlet_name)
            watt = self.outlet.get_power(outlet_name)
            #print(f"  [house] outlet {outlet_name} state: {is_on}")
            #is_on = state["state"]
            outlet_states[outlet_name] = {
                "is_on": is_on,
                "power": watt
            }
        return outlet_states

    def get_bulb_names(self):
        return self.bulb_names

    def get_bulb_names_string(self):
        return self.bulb_names_string

    def set_bulb_on_off(self, bulb_name, state):
        retVal = self.light.set_bulb_on_off(bulb_name, state)
        self.colors_changed()
        return retVal

    def get_bulb_on_off_state(self, bulb_name):
        return self.light.get_bulb_on_off_state(bulb_name)

    def set_color_hex(self, bulb_name, color_string):
        self.light.set_color_hex(bulb_name, color_string)
        self.colors_changed()

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
        # print("  [house] calling light.get_colors()")
        self.light.get_colors()
        # print("  [house] calling wled.bulb_colors_changed()")
        colors = self.light.get_colors_json_rgb()
        # print("  [house] calling wled.bulb_colors_changed()")
        self.wled.bulb_colors_changed(colors)
        # print("  [house] finished colors_changed()")


logic = HouseLogic()
