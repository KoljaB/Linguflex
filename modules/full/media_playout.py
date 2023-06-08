import sys
sys.path.insert(0, '..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from media_playout_helper import YoutubeManagement

playout_action = {
    'description': 'Musik oder Videos abspielen',
    'react_to': ['spiel', 'lied', 'song', 'album', 'alben', 'musik', 'video', 'clip', 'filme', 'film', 'stream', 'streaming', 'audio', 'sound', 'playlist', 'titel', 'track', 'medien', 'künstler', 'interpret', 'band', 'youtube', 'hörbuch', 'hörbücher', 'podcast', 'podcasts'],
    'example_user': 'Spiel Abbey Road von den Beatles',
    'example_assistant': 'Ok, ich spiele nun das Album "Abbey Road" von den Beatles {"Playout":"Beatles Abbey Road full album"}',
    'key_description': '"Playout"',
    'value_description': 'Name des auszuspielenden Werks (Song, Album, Video)',
    'keys': ['Playout'],
    'instructions' : 'Im Zweifel Namen ausdenken. Für Alben nutze "full album".'
}

playout_stop_action = {
    'description': 'Abspiel von Musik oder Videos stoppen',
    'react_to': ['stopp', 'stop', 'stoppe', 'beende', 'ende', 'halt', 'halte', 'schluss', 'schluß'],
    'example_user': 'Stop!',
    'example_assistant': 'Ok, das Ausspiel wird beendet. {"PlayoutStop":"true"}',
    'key_description': '"PlayoutStop"',
    'value_description': '"true"',
    'keys': ['PlayoutStop'],
    'instructions' : ''
}

class MediaPlayoutModule(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [playout_action,playout_stop_action]
        self.playout = YoutubeManagement()

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'PlayoutStop' in json and json['PlayoutStop'] == 'true':
                log(DEBUG_LEVEL_MIN, '[playout] stop')
                self.playout.close()
            elif 'Playout' in json: 
                log(DEBUG_LEVEL_MIN, '[playout] start')
                self.playout.open(json['Playout'])
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [playout] ERROR:' + e)

    def shutdown(self) -> None:
        self.playout.shutdown()