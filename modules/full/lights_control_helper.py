import time
import tinytuya
import re
import colorsys
import threading
import json
from hmac import new
from typing import Tuple, Dict

from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message

set_section('lights_control')

class SmartBulbThread(threading.Thread):
    def __init__(self, 
            bulb_param: Dict[str, str],
            connection_event: threading.Event(), 
            status_event: threading.Event(), 
            color_change_condition: threading.Condition()) -> None:
        super().__init__()
        self.color_change_condition = color_change_condition
        self.color = (0, 0, 0)
        self.bulb_param = bulb_param
        self.connection_event = connection_event
        self.status_event = status_event
        self.state = 'off'
        self.is_running = True

    def change_color(self, 
            color: Tuple[int, int, int]) -> None:
        with self.color_change_condition:
            self.color = color
            self.color_change_condition.notify()        

    def shutdown(self) -> None:
        self.is_running = False

    def set_color(self, 
            rgb_tupel: Tuple[int, int, int]) -> None:
        self.color = rgb_tupel
        log(DEBUG_LEVEL_MAX, f'  [lights] {self.bulb_param["name"]} color set to: {rgb_tupel}')        
        self.device.set_colour(rgb_tupel[0], rgb_tupel[1], rgb_tupel[2], nowait=True)        
        
        # we don't ever flood the bulb, so safest bet is forcewait after set color
        time.sleep(0.2) 

    def run(self) -> None:
        name = self.bulb_param["name"]
        id = self.bulb_param['id']
        ip = self.bulb_param['ip']
        key = self.bulb_param['key']
        deviceVersion = float(self.bulb_param['v'])
        # Connect to tuya bulb
        self.device = tinytuya.BulbDevice(id, ip, key)
        self.device.set_version(deviceVersion)
        log(DEBUG_LEVEL_MAX, f'  [lights] {name} connected')        
        self.connection_event.set()
        # Get status of bulb    
        data = self.device.status()
        if 'dps' in data:
            self.state = 'on'
            dps = data['dps']
            color = dps['24']
            self.color = self.hsv_string_to_rgb(color)
        log(DEBUG_LEVEL_MAX, f'  [lights] {name} color: {self.color}')
        self.status_event.set()
        # Enter worker cycle
        while self.is_running:
            with self.color_change_condition:
                notified = self.color_change_condition.wait(timeout=0.5)  # Set a timeout of 0.5 seconds
                if notified:
                    self.set_color(self.color)
                time.sleep(0.01)

    def hsv_string_to_rgb(self,
            hsv: str) -> Tuple[int, int, int]:
        color_value = int(hsv[0:4], 16)
        saturation_value = int(hsv[4:8], 16)
        brightness_value = int(hsv[8:12], 16) 
        # convert to values between 0 and 1
        color_value = color_value / 360.0
        saturation_value = saturation_value / 1000.0
        brightness_value = brightness_value / 1000.0
        # calculate rgb from hsv values
        hsv = (color_value, saturation_value, brightness_value)
        rgb = colorsys.hsv_to_rgb(*hsv)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

class LightManager():
    def __init__(self) -> None:
        self.is_running = True
        self.is_rotation_active = False
        self.rotation_speed = 10
        self.rotation_update_pause = 0.5
        self.rotation_clockwise = True
        self.bulb_devices = []
        self.bulb_states = []
        self.bulb_colors = []
        self.bulb_rotation_colors = []
        self.get_bulb_params()
        num_lamps = len(self.bulb_params)
        # Create event objects
        self.connection_events = [threading.Event() for _ in range(num_lamps)]
        self.status_events = [threading.Event() for _ in range(num_lamps)]
        color_change_conditions = [threading.Condition() for _ in range(num_lamps)]
        # Create and start lamp threads
        self.bulb_threads = [SmartBulbThread(self.bulb_params[i], self.connection_events[i], self.status_events[i], color_change_conditions[i]) for i in range(num_lamps)]
        for thread in self.bulb_threads:
            self.bulb_colors.append((0,0,0))
            thread.start()
        new_rgb_color = (255, 0, 0)  # Beispiel: Rote Farbe
        for thread in self.bulb_threads:
            thread.change_color(new_rgb_color)
        self.rotation_worker_thread = threading.Thread(target=self.rotation_worker)
        self.rotation_worker_thread.start()

    def shutdown(self) -> None:
        self.is_running = False
        for thread in self.bulb_threads:
            thread.shutdown()
        # Wait for all threads to finish
        for thread in self.bulb_threads:
            thread.join()

    def wait_ready(self) -> None:
        # Wait for all bulbs connected
        log(DEBUG_LEVEL_MAX, '  [lights] connecting to bulbs')
        for event in self.connection_events:
            event.wait()
        log(DEBUG_LEVEL_MID, '  [lights] bulbs connected')
        # Wait for all bulbs status requested
        for event in self.status_events:
            event.wait()
        log(DEBUG_LEVEL_MID, '  [lights] bulbs status check complete')
        # Init colors
        for bulb_thread in self.bulb_threads:
            i = self.find_bulb_index(bulb_thread.bulb_param['name'])
            self.bulb_colors[i] = bulb_thread.color

    def set_colors_json_hex_string(self, 
            json: str) -> None:
        data = json.loads(json)
        self.set_colors_json_hex(data)

    def find_bulb_index(self, 
            name: str) -> int:
        for bulb in self.bulb_params:
            if bulb['name'] == name:
                index = self.bulb_params.index(bulb)
                return index
        return -1
    
    def set_colors_json_hex(self, 
            data) -> None:
        for i, bulb in enumerate(self.bulb_params):
            name = bulb['name']
            if name in data:
                hex_color = data[name]
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
                self.set_color(name, rgb_color)

    def set_color(self, 
            bulb_name: str, 
            color: Tuple[int, int, int]) -> None:
        i = self.find_bulb_index(bulb_name)
        self.bulb_colors[i] = color
        for bulb_thread in self.bulb_threads:
            if bulb_thread.bulb_param['name'] == bulb_name:
                bulb_thread.change_color(color)
                break

    def get_color(self, 
            bulb_name: str) -> Tuple[int, int, int]:
        for bulb_thread in self.bulb_threads:
            if bulb_thread.bulb_param['name'] == bulb_name:
                i = self.find_bulb_index(bulb_name)
                self.bulb_colors[i] = bulb_thread.color
                return self.bulb_colors[i]

    def rotate(self, 
            speed = 10, 
            update_pause = 0.5, 
            clockwise = True):
        self.bulb_rotation_colors = []
        # Make a copy of the original bulb_colors list to perform rotation.
        for bulb in self.bulb_params:
            bulbname = bulb['name']
            color = self.get_color(bulbname)                    
            self.bulb_rotation_colors.append(color)
        self.rotation_speed = float(speed)
        self.rotation_update_pause = float(update_pause)
        self.rotation_clockwise = clockwise        
        self.is_rotation_active = True
    
    def rotation_worker(self) -> None:
        cycle = 0
        while self.is_running:
            if self.is_rotation_active:
                if cycle == 0: 
                    cycle = self.rotation_speed
                    original_colors = self.bulb_rotation_colors.copy()
                cycle_percent = (self.rotation_speed - cycle) / self.rotation_speed
                cycle -= 1
                # Calculate the new colors and update the bulbs.
                for i in range(len(self.bulb_params)):
                    # Determine the neighboring color index based on the rotation direction.
                    if self.rotation_clockwise:
                        next_idx = (i + 1) % len(self.bulb_params)
                    else:
                        next_idx = (i - 1) % len(self.bulb_params)
                    # Interpolate the color
                    new_color = self.interpolate_color(original_colors[i], original_colors[next_idx], cycle_percent)
                    bulbname = self.bulb_params[i]['name']
                    self.set_color(bulbname, new_color)                    
                if cycle == 0: 
                     if self.rotation_clockwise:
                        first_item = self.bulb_rotation_colors[0]
                        self.bulb_rotation_colors = self.bulb_rotation_colors[1:] + [first_item]
                     else:
                        last_item = self.bulb_rotation_colors[-1]
                        self.bulb_rotation_colors = [last_item] + self.bulb_rotation_colors[:-1]
            time.sleep(self.rotation_update_pause)

    def get_bulb_params(self) -> None:
        self.bulb_params = []
        try:
            bulb_names = cfg[get_section()].get('bulb_names').split(',')
            bulb_ids = cfg[get_section()].get('bulb_ids').split(',')
            bulb_ips = cfg[get_section()].get('bulb_ips').split(',')
            bulb_keys = cfg[get_section()].get('bulb_keys').split(',')
            bulb_versions = cfg[get_section()].get('bulb_versions').split(',')
        except Exception as e:
            raise ValueError(configuration_parsing_error_message + ' ' + str(e))        
        for i in range(len(bulb_names)):
            bulb_param = {
                'name': bulb_names[i],
                'id': bulb_ids[i],
                'ip': bulb_ips[i],
                'key': bulb_keys[i],
                'v': bulb_versions[i]
            }
            self.bulb_params.append(bulb_param)

    def get_names(self) -> str:
        return [entry['name'] for entry in self.bulb_params]

    def stop(self) -> None:
        self.is_rotation_active = False

    def get_colors_json_rgb(self):
        compressed_data = {}
        for i, color in enumerate(self.bulb_colors):
            name = self.bulb_params[i]['name']
            compressed_data[name] = color
        return json.dumps(compressed_data, separators=(',', ':'))            
    
    def get_colors_json_hex(self):
        compressed_data = {}
        for i, color in enumerate(self.bulb_colors):
            name = self.bulb_params[i]['name']
            hex_color = '#{:02X}{:02X}{:02X}'.format(*color)
            compressed_data[name] = hex_color
        return json.dumps(compressed_data, separators=(',', ':'))    

    def interpolate_color(self, 
            color1: Tuple[int, int, int], 
            color2: Tuple[int, int, int], 
            interpolationGrade: float) -> Tuple[int, int, int]:
        rDist = color2[0] - color1[0]
        gDist = color2[1] - color1[1]
        bDist = color2[2] - color1[2]
        r = int(color1[0] + interpolationGrade * rDist)
        g = int(color1[1] + interpolationGrade * gDist)
        b = int(color1[2] + interpolationGrade * bDist)
        return (r, g, b)            
    
    # convert hhhhssssvvvv hsv color string to (R, G, B)
    def hsv_string_to_rgb(self, 
            hsv: str) -> Tuple[int, int, int]:
        color_value = int(hsv[0:4], 16)
        saturation_value = int(hsv[4:8], 16)
        brightness_value = int(hsv[8:12], 16)
        # convert to values between 0 and 1
        color_value = color_value / 360.0
        saturation_value = saturation_value / 1000.0
        brightness_value = brightness_value / 1000.0
        # calculate rgb from hsv values
        hsv = (color_value, saturation_value, brightness_value)
        rgb = colorsys.hsv_to_rgb(*hsv)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))