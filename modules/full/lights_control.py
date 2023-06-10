import sys
sys.path.insert(0, '..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from lights_control_helper import LightManager

set_lights_action = {
    'description': 'Lichtfarben der Lampen ändern',
    'react_to': ['lampe', 'lampen', 'licht', 'lichter', 'farbe', 'farben', 'stimmung', 'beleuchtung', 'lichtstimmung', 'lichtfarbe', 'lichtwechsel', 'lichtquelle', 'leuchte', 'leuchten', 'ambiente', 'atmosphäre', 'helligkeit', 'dimmen', 'dimme', 'einstellen', 'regulier', 'reguliere', 'regel', 'farbwechsel', 'farbton'],
    'example_user': 'Licht am PC rot und an der Tür blau',
    'example_assistant': 'Das Licht am PC ist nun rot und das an der Tür blau {"PC":"#FF0000","Tuer":"#0000FF"}',
    'key_description': 'Name der Lampe (zB "Tuer","PC")',
    'value_description': 'Farbcode in Hex (zB "#FF0000")',
    'keys': [],
    'instructions' : ''
}

rotate_lights_action = {
    'description': 'Lichtfarben der Lampen rotieren lassen',
    'react_to': ['rotation', 'rotiere', 'rotier', 'karussell', 'uhrzeigersinn', 'anders herum', 'drehe', 'linksherum', 'links herum', 'rechtsherum', 'rechts herum', 'disco', 'disko'],
    'example_user': 'Drehe die Farben gegen den Uhrzeigersinn',
    'example_assistant': 'Die Farben drehen sich nun gegen den Uhrzeigersinn. {"Rotate":"counterclockwise"}',
    'key_description': '"Rotate"',
    'value_description': 'Drehrichtung, entweder "clockwise" oder "counterclockwise"',
    'keys': ['Rotate'],
    'instructions' : ''
}

stop_rotate_lights_action = {
    'description': 'Rotation der Lichtfarben der Lampen stoppen',
    'react_to': ['stopp', 'stop', 'stoppe', 'beende', 'ende', 'halt', 'halte', 'schluss', 'schluß'],
    'example_user': 'Beende die Rotation der Farben',
    'example_assistant': 'Die Farben drehen sich nun nicht mehr. {"RotateStop":"true"}',
    'key_description': '"RotateStop"',
    'value_description': '"true"',
    'keys': ['RotateStop'],
    'instructions' : ''
}

class LightsModule(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [set_lights_action, rotate_lights_action, stop_rotate_lights_action]        
        self.light = LightManager()
        self.light.wait_ready() # blocking call
        set_lights_action['keys'] = self.light.get_names()

    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
        set_lights_action['instructions'] = 'Im Zweifel Farben ausdenken. Alle verfügbaren Lampen und ihre aktuellen Farben: ' + self.light.get_colors_json_hex()
    
    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'RotateStop' in json and json['RotateStop'] == 'true':
                log(DEBUG_LEVEL_MID, '  [lights] rotation stopped')
                self.light.stop()
            elif 'Rotate' in json: 
                log(DEBUG_LEVEL_MID, '  [lights] rotating colors')
                clockwise = json['Rotate'] == 'clockwise'
                self.light.rotate(10, 0.5, clockwise)
            else:
                log(DEBUG_LEVEL_MIN, '[lights] setting colors')
                self.light.set_colors_json_hex(json)
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [lights] ERROR:' + e)

    def shutdown(self) -> None:
        self.light.shutdown()          