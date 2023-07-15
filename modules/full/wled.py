import json
import requests
import os
from core import BaseModule, Request, log, cfg, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX

from typing import List, Tuple

wled_url = cfg('wled_url')
max_bulbs = int(cfg('max_bulbs', 300))

class WLED(BaseModule):   
    def __init__(self) -> None: 
        self.max_bulbs = max_bulbs
        self.colors = []
        self.indices = []

        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_directory, "wled.json")
        file_path = "config/wled.json"

        with open(file_path, "r") as read_file:
            self.bulb_data = json.load(read_file)        

    def init(self) -> None: 
        def bulb_colors_changed(bulb_colors): 
            self.bulb_colors = bulb_colors
            self.interpolate_colors()
        self.server.register_event("bulb_colors_changed", bulb_colors_changed)

    def interpolate_colors(self):
        self.resetcolors()

        for bulb in self.bulb_data:
            name = bulb['name']
            index = bulb['index']
            if name in self.bulb_colors:
                self.addcolor(self.bulb_colors[name], index)        
                
        self.interpolate()   

    def set_max_bulbs(self, 
            max_bulbs: int) -> None: 
        self.max_bulbs = max_bulbs

    def resetcolors(self) -> None: 
        self.colors.clear()
        self.indices.clear()

    def addcolor(self,
            rgb: Tuple[int, int, int], 
            index: int) -> None: 
        log(DEBUG_LEVEL_MAX, f'  [wled] add color {rgb} at {index}')
        self.colors.append(rgb)
        self.indices.append(index)

    def interpolate(self) -> None:
        colors = []
        if len(self.indices) > 0:
            for i in range(self.indices[0]):
                colors.append(self.colors[0])
        if len(self.indices) > 1:
            for i in range(len(self.indices) - 1):
                diff = self.indices[i+1] - self.indices[i]
                for led_index in range(diff):
                    color = self.interpolate_color(self.colors[i], self.colors[i+1], led_index / diff)
                    colors.append(color)
        if len(self.indices) > 0:
            remaining_bulbs_count = self.max_bulbs - self.indices[len(self.indices)-1]
            for i in range(remaining_bulbs_count):
                colors.append(self.colors[len(self.colors)-1])
        self.set_wled_colors(colors)

    def convert_to_hex(self, 
            color: Tuple[int, int, int]) -> str:
        return f'{color[0]:02x}{color[1]:02x}{color[2]:02x}'

    def set_wled_colors(self, 
            colors: List[tuple]) -> None:
        json_start = '{"seg":{"i":['
        json_end = ']}}'
        json_colors = ''
        for i, color in enumerate(colors):
            json_colors += f'"{self.convert_to_hex(color)}"'
            if i < len(colors) - 1:
                json_colors += ', '
        complete_json = json_start + json_colors + json_end
        self.simple_json_post(wled_url, complete_json)

    def simple_json_post(self, 
            url: str, json: str) -> None:
        headers = {'Content-Type': 'application/json'}
        try:
            log(DEBUG_LEVEL_MAX, f'  [wled] setting colors') # {json}
            response = requests.post(url, data=json, headers=headers)
            if response.status_code == 200:
                result = response.text
                log(DEBUG_LEVEL_MAX, f'  [wled] response: {result}') 
        except Exception as ex:
            log(DEBUG_LEVEL_MIN, f'[wled] ERROR sending json {json}, error: {str(ex)}') 

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